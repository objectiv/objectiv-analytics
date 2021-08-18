const path = require('path');

const COMPONENT_ATTRIBUTE = 'data-objectiv-component';
const FILE_NAME_ATTRIBUTE = 'data-objectiv-file-name';
const TRACK_CLICK_ATTRIBUTE = 'data-objectiv-track-click';

function isReactFragment(openingElement) {
  return (
    openingElement.node.name.name === 'Fragment' ||
    (openingElement.node.name.type === 'JSXMemberExpression' &&
      openingElement.node.name.object.name === 'React' &&
      openingElement.node.name.property.name === 'Fragment')
  );
}

function getFileNameFromState(state) {
  const name = state.file.opts.parserOpts.sourceFileName;
  if (typeof name !== 'string') {
    return undefined;
  }
  if (name.indexOf('/') !== -1) {
    return name.split('/').pop();
  } else if (name.indexOf('\\') !== -1) {
    return name.split('\\').pop();
  } else {
    return name;
  }
}

function isJSXAttributeSet({ jsxElement, name }) {
  return jsxElement.node.attributes.find((attribute) => {
    if (!attribute.name) {
      return false;
    }
    return attribute.name.name === name;
  });
}

function addJSXAttribute({ types, jsxElement, name, value }) {
  if (!value) {
    return false;
  }

  if (isReactFragment(jsxElement)) {
    return false;
  }

  if (isJSXAttributeSet({ jsxElement, name })) {
    return false;
  }

  if (!jsxElement.node.attributes) {
    jsxElement.node.attributes = {};
  }

  jsxElement.node.attributes.push(types.JSXAttribute(types.jSXIdentifier(name), types.stringLiteral(value)));
}

function processJSXElements({ node, component, fileName, types }) {
  node.traverse({
    JSXOpeningElement(jsxElement) {
      // TODO we could improve this to add the attributes only to tracked elements
      // TODO we could improve this and add the ID, ContextType and ContextId also to third party components
      addJSXAttribute({ types, jsxElement, name: COMPONENT_ATTRIBUTE, value: component });
      addJSXAttribute({ types, jsxElement, name: FILE_NAME_ATTRIBUTE, value: fileName });

      // TODO we could improve this to monitor other handlers as well
      const isInteractive = isJSXAttributeSet({ jsxElement, name: 'onClick' });
      addJSXAttribute({ types, jsxElement, name: TRACK_CLICK_ATTRIBUTE, value: isInteractive ? 'true' : 'false' });
    },
  });
}

module.exports = function ({ types }) {
  return {
    visitor: {
      ArrowFunctionExpression(arrowFunctionExpression, state) {
        const isAnonymous = !(arrowFunctionExpression.parent.id && arrowFunctionExpression.parent.id.name);
        const isExportDefault = arrowFunctionExpression.parentPath.isExportDefaultDeclaration();

        // Skipping ArrowFunctionExpression without parent.id.name
        if (isAnonymous && !isExportDefault) {
          return false;
        }

        const fileName = getFileNameFromState(state);

        let component = null;
        if (!isAnonymous && !isExportDefault) {
          component = arrowFunctionExpression.parent.id.name;
        } else {
          component = path.parse(fileName).name;
        }

        processJSXElements({
          node: arrowFunctionExpression,
          component,
          fileName,
          types,
        });
      },

      FunctionDeclaration(functionDeclaration, state) {
        // Skipping FunctionDeclaration without node.id.name
        if (!functionDeclaration.node.id || !functionDeclaration.node.id.name) {
          return false;
        }

        const fileName = getFileNameFromState(state);

        processJSXElements({
          node: functionDeclaration,
          component: functionDeclaration.node.id.name,
          fileName,
          types,
        });
      },

      ClassDeclaration(classDeclaration, state) {
        // Skipping ClassDeclaration without node.id.name
        if (!classDeclaration.node.id || !classDeclaration.node.id.name) {
          return false;
        }

        const fileName = getFileNameFromState(state);

        classDeclaration.traverse({
          ClassMethod(classMethod) {
            if (classMethod.node.key.name === 'render') {
              classMethod.traverse({
                ReturnStatement(returnStatement) {
                  const returnValue = returnStatement.get('argument');
                  if (returnValue.isJSXElement()) {
                    processJSXElements({
                      node: returnValue,
                      component: classDeclaration.node.id.name,
                      fileName,
                      types,
                    });
                  }
                },
              });
            }
          },
        });
      },
    },
  };
};
