export const testScript = {
  fileName: 'http://localhost:3000/test.js',
  sourceCode: `// modules are defined as an array
// [ module function, map of requires ]
//
// map of requires is short require name -> numeric require
//
// anything defined in a previous bundle is accessed via the
// orig method which is the require for previous bundles
parcelRequire = (function (modules, cache, entry, globalName) {
  // Save the require from previous bundle to this closure if any
  var previousRequire = typeof parcelRequire === 'function' && parcelRequire;
  var nodeRequire = typeof require === 'function' && require;

  function newRequire(name, jumped) {
    if (!cache[name]) {
      if (!modules[name]) {
        // if we cannot find the module within our internal map or
        // cache jump to the current global require ie. the last bundle
        // that was added to the page.
        var currentRequire = typeof parcelRequire === 'function' && parcelRequire;
        if (!jumped && currentRequire) {
          return currentRequire(name, true);
        }

        // If there are other bundles on this page the require from the
        // previous one is saved to 'previousRequire'. Repeat this as
        // many times as there are bundles until the module is found or
        // we exhaust the require chain.
        if (previousRequire) {
          return previousRequire(name, true);
        }

        // Try the node require function if it exists.
        if (nodeRequire && typeof name === 'string') {
          return nodeRequire(name);
        }

        var err = new Error('Cannot find module \\'' + name + '\\'');
        err.code = 'MODULE_NOT_FOUND';
        throw err;
      }

      localRequire.resolve = resolve;
      localRequire.cache = {};

      var module = cache[name] = new newRequire.Module(name);

      modules[name][0].call(module.exports, localRequire, module, module.exports, this);
    }

    return cache[name].exports;

    function localRequire(x){
      return newRequire(localRequire.resolve(x));
    }

    function resolve(x){
      return modules[name][1][x] || x;
    }
  }

  function Module(moduleName) {
    this.id = moduleName;
    this.bundle = newRequire;
    this.exports = {};
  }

  newRequire.isParcelRequire = true;
  newRequire.Module = Module;
  newRequire.modules = modules;
  newRequire.cache = cache;
  newRequire.parent = previousRequire;
  newRequire.register = function (id, exports) {
    modules[id] = [function (require, module) {
      module.exports = exports;
    }, {}];
  };

  var error;
  for (var i = 0; i < entry.length; i++) {
    try {
      newRequire(entry[i]);
    } catch (e) {
      // Save first error but execute all entries
      if (!error) {
        error = e;
      }
    }
  }

  if (entry.length) {
    // Expose entry point to Node, AMD or browser globals
    // Based on https://github.com/ForbesLindesay/umd/blob/master/template.js
    var mainExports = newRequire(entry[entry.length - 1]);

    // CommonJS
    if (typeof exports === "object" && typeof module !== "undefined") {
      module.exports = mainExports;

    // RequireJS
    } else if (typeof define === "function" && define.amd) {
     define(function () {
       return mainExports;
     });

    // <script>
    } else if (globalName) {
      this[globalName] = mainExports;
    }
  }

  // Override the current require with this new one
  parcelRequire = newRequire;

  if (error) {
    // throw error from earlier, _after updating parcelRequire_
    throw error;
  }

  return newRequire;
})({"HdJB":[function(require,module,exports) {
var function1 = function function1() {
  console.log('function 1');
};

function function2() {
  console.log('function 2');
}

var function3 = function function3() {
  console.log('function 3');
};

var oneTwoThree = eval("123");

var notGonnaWork = function notGonnaWork() {
  return eval("ABC");
};
},{}]},{},["HdJB"], null)
//# sourceMappingURL=/test.js.map`,
  sourceMappingURL: 'test.js.map',
  sourceMap: JSON.stringify({
    version: 3,
    sources: ['test.js'],
    names: ['function1', 'console', 'log', 'function2', 'function3', 'oneTwoThree', 'eval', 'notGonnaWork'],
    mappings:
      ';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;AAAA,IAAMA,SAAS,GAAG,SAAZA,SAAY,GAAY;AAC5BC,EAAAA,OAAO,CAACC,GAAR,CAAY,YAAZ;AACD,CAFD;;AAGA,SAASC,SAAT,GAAoB;AAClBF,EAAAA,OAAO,CAACC,GAAR,CAAY,YAAZ;AACD;;AACD,IAAME,SAAS,GAAG,SAAZA,SAAY,GAAM;AACtBH,EAAAA,OAAO,CAACC,GAAR,CAAY,YAAZ;AACD,CAFD;;AAGA,IAAMG,WAAW,GAAGC,IAAI,CAAC,KAAD,CAAxB;;AACA,IAAMC,YAAY,GAAG,SAAfA,YAAe;AAAA,SAAMD,IAAI,CAAC,KAAD,CAAV;AAAA,CAArB',
    file: 'test.js',
    sourceRoot: '..',
    sourcesContent: [
      "const function1 = function () {\n  console.log('function 1')\n};\nfunction function2(){\n  console.log('function 2');\n}\nconst function3 = () => {\n  console.log('function 3');\n}\nconst oneTwoThree = eval(\"123\");\nconst notGonnaWork = () => eval(\"ABC\");\n",
    ],
  }),
};

export const chrome_91 = {
  stackTrace: `Error
at DebugTransport.handle (http://localhost:3000/static/js/vendors~main.chunk.js:45087:22)
at http://localhost:3000/static/js/vendors~main.chunk.js:44297:35
at Array.map (<anonymous>)
at TransportGroup.<anonymous> (http://localhost:3000/static/js/vendors~main.chunk.js:44296:33)
at step (http://localhost:3000/static/js/vendors~main.chunk.js:43482:17)
at Object.next (http://localhost:3000/static/js/vendors~main.chunk.js:43413:14)
at http://localhost:3000/static/js/vendors~main.chunk.js:43385:67
at new Promise (<anonymous>)
at __awaiter$1 (http://localhost:3000/static/js/vendors~main.chunk.js:43364:10)
at TransportGroup.handle (http://localhost:3000/static/js/vendors~main.chunk.js:44286:12)
at ReactTracker.<anonymous> (http://localhost:3000/static/js/vendors~main.chunk.js:43760:30)
at step (http://localhost:3000/static/js/vendors~main.chunk.js:43482:17)
at Object.next (http://localhost:3000/static/js/vendors~main.chunk.js:43413:14)
at http://localhost:3000/static/js/vendors~main.chunk.js:43385:67
at new Promise (<anonymous>)
at __awaiter$1 (http://localhost:3000/static/js/vendors~main.chunk.js:43364:10)
at ReactTracker.Tracker.trackEvent (http://localhost:3000/static/js/vendors~main.chunk.js:43732:12)
at http://localhost:3000/static/js/vendors~main.chunk.js:45389:13
at invokePassiveEffectCreate (http://localhost:3000/static/js/vendors~main.chunk.js:95512:24)
at HTMLUnknownElement.callCallback (http://localhost:3000/static/js/vendors~main.chunk.js:76128:18)
at Object.invokeGuardedCallbackDev (http://localhost:3000/static/js/vendors~main.chunk.js:76177:20)
at invokeGuardedCallback (http://localhost:3000/static/js/vendors~main.chunk.js:76237:35)
at flushPassiveEffectsImpl (http://localhost:3000/static/js/vendors~main.chunk.js:95594:13)
at unstable_runWithPriority (http://localhost:3000/static/js/vendors~main.chunk.js:111552:16)
at runWithPriority$1 (http://localhost:3000/static/js/vendors~main.chunk.js:83534:14)
at flushPassiveEffects (http://localhost:3000/static/js/vendors~main.chunk.js:95471:18)
at performSyncWorkOnRoot (http://localhost:3000/static/js/vendors~main.chunk.js:94311:7)
at http://localhost:3000/static/js/vendors~main.chunk.js:83588:30
at unstable_runWithPriority (http://localhost:3000/static/js/vendors~main.chunk.js:111552:16)
at runWithPriority$1 (http://localhost:3000/static/js/vendors~main.chunk.js:83534:14)
at flushSyncCallbackQueueImpl (http://localhost:3000/static/js/vendors~main.chunk.js:83583:13)
at flushSyncCallbackQueue (http://localhost:3000/static/js/vendors~main.chunk.js:83571:7)
at unbatchedUpdates (http://localhost:3000/static/js/vendors~main.chunk.js:94482:11)
at legacyRenderSubtreeIntoContainer (http://localhost:3000/static/js/vendors~main.chunk.js:97991:9)
at Object.render (http://localhost:3000/static/js/vendors~main.chunk.js:98074:14)
at http://localhost:3000/static/js/main.chunk.js:6486:52`,

  stackFrames: [
    {
      columnNumber: 22,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'DebugTransport.handle',
      lineNumber: 45087,
    },
    {
      columnNumber: 35,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: '<anonymous>',
      lineNumber: 44297,
    },
    {
      columnNumber: 33,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'TransportGroup.<anonymous>',
      lineNumber: 44296,
    },
    {
      columnNumber: 17,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'step',
      lineNumber: 43482,
    },
    {
      columnNumber: 14,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'Object.next',
      lineNumber: 43413,
    },
    {
      columnNumber: 67,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: '<anonymous>',
      lineNumber: 43385,
    },
    {
      columnNumber: 10,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: '__awaiter$1',
      lineNumber: 43364,
    },
    {
      columnNumber: 12,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'TransportGroup.handle',
      lineNumber: 44286,
    },
    {
      columnNumber: 30,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'ReactTracker.<anonymous>',
      lineNumber: 43760,
    },
    {
      columnNumber: 17,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'step',
      lineNumber: 43482,
    },
    {
      columnNumber: 14,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'Object.next',
      lineNumber: 43413,
    },
    {
      columnNumber: 67,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: '<anonymous>',
      lineNumber: 43385,
    },
    {
      columnNumber: 10,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: '__awaiter$1',
      lineNumber: 43364,
    },
    {
      columnNumber: 12,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'ReactTracker.Tracker.trackEvent',
      lineNumber: 43732,
    },
    {
      columnNumber: 13,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: '<anonymous>',
      lineNumber: 45389,
    },
    {
      columnNumber: 24,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'invokePassiveEffectCreate',
      lineNumber: 95512,
    },
    {
      columnNumber: 18,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'HTMLUnknownElement.callCallback',
      lineNumber: 76128,
    },
    {
      columnNumber: 20,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'Object.invokeGuardedCallbackDev',
      lineNumber: 76177,
    },
    {
      columnNumber: 35,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'invokeGuardedCallback',
      lineNumber: 76237,
    },
    {
      columnNumber: 13,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'flushPassiveEffectsImpl',
      lineNumber: 95594,
    },
    {
      columnNumber: 16,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'unstable_runWithPriority',
      lineNumber: 111552,
    },
    {
      columnNumber: 14,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'runWithPriority$1',
      lineNumber: 83534,
    },
    {
      columnNumber: 18,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'flushPassiveEffects',
      lineNumber: 95471,
    },
    {
      columnNumber: 7,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'performSyncWorkOnRoot',
      lineNumber: 94311,
    },
    {
      columnNumber: 30,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: '<anonymous>',
      lineNumber: 83588,
    },
    {
      columnNumber: 16,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'unstable_runWithPriority',
      lineNumber: 111552,
    },
    {
      columnNumber: 14,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'runWithPriority$1',
      lineNumber: 83534,
    },
    {
      columnNumber: 13,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'flushSyncCallbackQueueImpl',
      lineNumber: 83583,
    },
    {
      columnNumber: 7,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'flushSyncCallbackQueue',
      lineNumber: 83571,
    },
    {
      columnNumber: 11,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'unbatchedUpdates',
      lineNumber: 94482,
    },
    {
      columnNumber: 9,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'legacyRenderSubtreeIntoContainer',
      lineNumber: 97991,
    },
    {
      columnNumber: 14,
      fileName: 'http://localhost:3000/static/js/vendors~main.chunk.js',
      functionName: 'Object.render',
      lineNumber: 98074,
    },
    {
      columnNumber: 52,
      fileName: 'http://localhost:3000/static/js/main.chunk.js',
      functionName: '<anonymous>',
      lineNumber: 6486,
    },
  ],
};

export const firefox_90 = {
  stackTrace: `./node_modules/@objectiv/tracker-react/dist/index.js/DebugTransport</DebugTransport.prototype.handle@http://localhost:3000/static/js/vendors~main.chunk.js:45087:22
./node_modules/@objectiv/tracker-react/dist/index.js/TransportGroup</TransportGroup.prototype.handle/</</<@http://localhost:3000/static/js/vendors~main.chunk.js:44297:35
./node_modules/@objectiv/tracker-react/dist/index.js/TransportGroup</TransportGroup.prototype.handle/</<@http://localhost:3000/static/js/vendors~main.chunk.js:44296:33
step@http://localhost:3000/static/js/vendors~main.chunk.js:43482:17
verb/<@http://localhost:3000/static/js/vendors~main.chunk.js:43413:14
__awaiter$1/<@http://localhost:3000/static/js/vendors~main.chunk.js:43385:67
__awaiter$1@http://localhost:3000/static/js/vendors~main.chunk.js:43364:10
./node_modules/@objectiv/tracker-react/dist/index.js/TransportGroup</TransportGroup.prototype.handle@http://localhost:3000/static/js/vendors~main.chunk.js:44286:12
./node_modules/@objectiv/tracker-react/dist/index.js/Tracker</Tracker.prototype.trackEvent/</<@http://localhost:3000/static/js/vendors~main.chunk.js:43760:30
step@http://localhost:3000/static/js/vendors~main.chunk.js:43482:17
broken
verb/<@http://localhost:3000/static/js/vendors~main.chunk.js:43413:14
__awaiter$1/<@http://localhost:3000/static/js/vendors~main.chunk.js:43385:67
__awaiter$1@http://localhost:3000/static/js/vendors~main.chunk.js:43364:10
./node_modules/@objectiv/tracker-react/dist/index.js/Tracker</Tracker.prototype.trackEvent@http://localhost:3000/static/js/vendors~main.chunk.js:43732:12
useTrackOnMount/<@http://localhost:3000/static/js/vendors~main.chunk.js:45389:13
invokePassiveEffectCreate@http://localhost:3000/static/js/vendors~main.chunk.js:95512:24
callCallback@http://localhost:3000/static/js/vendors~main.chunk.js:76128:18
invokeGuardedCallbackDev@http://localhost:3000/static/js/vendors~main.chunk.js:76177:20
invokeGuardedCallback@http://localhost:3000/static/js/vendors~main.chunk.js:76237:35
flushPassiveEffectsImpl@http://localhost:3000/static/js/vendors~main.chunk.js:95594:34
unstable_runWithPriority@http://localhost:3000/static/js/vendors~main.chunk.js:111552:16
runWithPriority$1@http://localhost:3000/static/js/vendors~main.chunk.js:83534:14
flushPassiveEffects@http://localhost:3000/static/js/vendors~main.chunk.js:95471:18
performSyncWorkOnRoot@http://localhost:3000/static/js/vendors~main.chunk.js:94311:7
flushSyncCallbackQueueImpl/<@http://localhost:3000/static/js/vendors~main.chunk.js:83588:30
unstable_runWithPriority@http://localhost:3000/static/js/vendors~main.chunk.js:111552:16
runWithPriority$1@http://localhost:3000/static/js/vendors~main.chunk.js:83534:14
flushSyncCallbackQueueImpl@http://localhost:3000/static/js/vendors~main.chunk.js:83583:30
flushSyncCallbackQueue@http://localhost:3000/static/js/vendors~main.chunk.js:83571:7
unbatchedUpdates@http://localhost:3000/static/js/vendors~main.chunk.js:94482:11
legacyRenderSubtreeIntoContainer@http://localhost:3000/static/js/vendors~main.chunk.js:97991:25
render@http://localhost:3000/static/js/vendors~main.chunk.js:98074:14
./src/index.js/</<@http://localhost:3000/static/js/main.chunk.js:6486:52
promise callback*./src/index.js/<@http://localhost:3000/static/js/main.chunk.js:6484:4
./src/index.js@http://localhost:3000/static/js/main.chunk.js:6579:30
__webpack_require__@http://localhost:3000/static/js/bundle.js:852:31
fn@http://localhost:3000/static/js/bundle.js:151:20
1@http://localhost:3000/static/js/main.chunk.js:6697:18
__webpack_require__@http://localhost:3000/static/js/bundle.js:852:31
checkDeferredModules@http://localhost:3000/static/js/bundle.js:46:23
webpackJsonpCallback@http://localhost:3000/static/js/bundle.js:33:19
@http://localhost:3000/static/js/main.chunk.js:1:59`,

  stackFrames: [
    // TODO
  ],
};
