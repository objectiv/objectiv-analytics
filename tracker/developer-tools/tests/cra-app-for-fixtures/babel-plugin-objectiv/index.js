const COMPONENT_NAME_ATTRIBUTE = 'data-objectiv-component';
const FILE_NAME_ATTRIBUTE = 'data-objectiv-file';

function isReactFragment(openingElement) {
  return (
    openingElement.node.name.name === 'Fragment' ||
    (openingElement.node.name.type === 'JSXMemberExpression' &&
      openingElement.node.name.object.name === 'React' &&
      openingElement.node.name.property.name === 'Fragment')
  );
}

function sourceFileNameFromState(state) {
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

function applyAttribute({ openingElement, types, componentName, fileName }) {
  if (!openingElement || isReactFragment(openingElement)) {
    return false;
  }

  const isComponentNameAlreadySet = openingElement.node.attributes.find((node) => {
    if (!node.name) {
      return false;
    }
    return node.name.name === COMPONENT_NAME_ATTRIBUTE;
  });

  const isFileNameAlreadySet = openingElement.node.attributes.find((node) => {
    if (!node.name) {
      return false;
    }
    return node.name.name === FILE_NAME_ATTRIBUTE;
  });

  if (!isComponentNameAlreadySet) {
    openingElement.node.attributes.push(
      types.jSXAttribute(types.jSXIdentifier(COMPONENT_NAME_ATTRIBUTE), types.stringLiteral(componentName))
    );
  }

  if (!isFileNameAlreadySet) {
    openingElement.node.attributes.push(
      types.jSXAttribute(types.jSXIdentifier(FILE_NAME_ATTRIBUTE), types.stringLiteral(fileName))
    );
  }
}

function functionBodyPushAttributes(types, path, componentName, fileName) {
  let openingElement = null;
  const functionBody = path.get('body').get('body');
  if (functionBody.parent && functionBody.parent.type === 'JSXElement') {
    const jsxElement = functionBody.find((c) => {
      return c.type === 'JSXElement';
    });
    if (!jsxElement) {
      return false;
    }
    openingElement = jsxElement.get('openingElement');
  } else {
    const returnStatement = functionBody.find((c) => {
      return c.type === 'ReturnStatement';
    });
    if (!returnStatement) {
      return false;
    }

    const arg = returnStatement.get('argument');
    if (!arg.isJSXElement()) {
      return false;
    }

    openingElement = arg.get('openingElement');
  }

  applyAttribute({ openingElement, types, componentName, fileName });
}

module.exports = function ({ types }) {
  return {
    visitor: {
      FunctionDeclaration(path, state) {
        if (!path.node.id || !path.node.id.name) {
          return false;
        }

        const componentName = path.node.id.name;
        const fileName = sourceFileNameFromState(state);

        functionBodyPushAttributes(types, path, componentName, fileName);
      },
      ArrowFunctionExpression(path, state) {
        if (!path.parent.id || !path.parent.id.name) {
          return false;
        }

        const componentName = path.parent.id.name;
        const fileName = sourceFileNameFromState(state);

        functionBodyPushAttributes(types, path, componentName, fileName);
      },
      ClassDeclaration(path, state) {
        const name = path.get('id');
        const properties = path.get('body').get('body');

        const render = properties.find((prop) => {
          return prop.isClassMethod() && prop.get('key').isIdentifier({ name: 'render' });
        });

        if (!render || !render.traverse) {
          return false;
        }

        render.traverse({
          ReturnStatement(returnStatement) {
            const arg = returnStatement.get('argument');
            if (!arg.isJSXElement()) {
              return false;
            }

            const openingElement = arg.get('openingElement');

            const componentName = name.node && name.node.name;
            const fileName = sourceFileNameFromState(state);

            applyAttribute({ openingElement, types, componentName, fileName });
          },
        });
      },
    },
  };
};
