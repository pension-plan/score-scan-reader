#!/usr/bin/env node
// Make @techstark/opencv-js 4.10.0-release.1 run under a CSP without 'unsafe-eval'.
//   node patch-noeval.js <in opencv.js> <out opencv.js>
// Emscripten's embind (in this build) creates every binding invoker with new Function(...);
// the claude.ai artifact CSP (script-src without 'unsafe-eval') rejects that, so cv never
// initialises. This rewrites the four code generators into equivalent closures (the same
// logic emscripten itself uses when built with -s DYNAMIC_EXECUTION=0). Exact-string
// replacements: the script fails loudly if the input is not the expected build.
const fs = require('fs');
const [, , inp, out] = process.argv;
let s = fs.readFileSync(inp, 'utf8');

function swapFn(name, replacement) {
  const i = s.indexOf('function ' + name + '(');
  if (i < 0) throw new Error('not found: ' + name);
  // the function body ends at the matching brace
  let k = s.indexOf('{', i), depth = 0, j = k;
  for (; j < s.length; j++) { const c = s[j]; if (c === '{') depth++; else if (c === '}') { depth--; if (!depth) break; } else if (c === '"' || c === "'") { const q = c; j++; while (s[j] !== q) { if (s[j] === '\\') j++; j++; } } }
  s = s.slice(0, i) + replacement + s.slice(j + 1);
}

swapFn('createNamedFunction', `function createNamedFunction(name,body){try{Object.defineProperty(body,"name",{value:makeLegalFunctionName(name)})}catch(e){}return body}`);

swapFn('craftInvokerFunction', `function craftInvokerFunction(humanName,argTypes,classType,cppInvokerFunc,cppTargetFunc){var argCount=argTypes.length;if(argCount<2){throwBindingError("argTypes array size mismatch! Must at least get return value and 'this' types!")}var isClassMethodFunc=argTypes[1]!==null&&classType!==null;var needsDestructorStack=false;for(var i=1;i<argTypes.length;++i){if(argTypes[i]!==null&&argTypes[i].destructorFunction===undefined){needsDestructorStack=true;break}}var returns=argTypes[0].name!=="void";var expected=argCount-2;var invoker=function(){if(arguments.length!==expected){throwBindingError("function "+humanName+" called with "+arguments.length+" arguments, expected "+expected+" args!")}var destructors=needsDestructorStack?[]:null;var wired=[cppTargetFunc];var thisWired;if(isClassMethodFunc){thisWired=argTypes[1].toWireType(destructors,this);wired.push(thisWired)}var argsWired=new Array(expected);for(var i=0;i<expected;++i){argsWired[i]=argTypes[i+2].toWireType(destructors,arguments[i]);wired.push(argsWired[i])}var rv=cppInvokerFunc.apply(null,wired);if(needsDestructorStack){runDestructors(destructors)}else{for(var i=isClassMethodFunc?1:2;i<argTypes.length;++i){var p=i===1?thisWired:argsWired[i-2];if(argTypes[i].destructorFunction!==null){argTypes[i].destructorFunction(p)}}}if(returns){return argTypes[0].fromWireType(rv)}};return createNamedFunction(humanName,invoker)}`);

swapFn('__emval_get_method_caller', `function __emval_get_method_caller(argCount,argTypes){var types=__emval_lookupTypes(argCount,argTypes);var retType=types[0];var caller=function(handle,name,destructors,args){var a=new Array(argCount-1);var offset=0;for(var i=0;i<argCount-1;++i){a[i]=types[1+i].readValueFromPointer(args+offset);offset+=types[i+1]["argPackAdvance"]}var rv=handle[name].apply(handle,a);for(var i=0;i<argCount-1;++i){if(types[i+1]["deleteObject"]){types[i+1].deleteObject(a[i])}}if(!retType.isVoid){return retType.toWireType(destructors,rv)}};return __emval_addMethodCaller(caller)}`);

// makeDynCaller is nested inside embind__requireFunction
const dynOld = /function makeDynCaller\(dynCall\)\{var args=\[\];.*?return new Function\("dynCall","rawFunction",body\)\(dynCall,rawFunction\)\}/s;
if (!dynOld.test(s)) throw new Error('not found: makeDynCaller');
s = s.replace(dynOld, 'function makeDynCaller(dynCall){return function(){var a=[rawFunction];for(var i=0;i<arguments.length;i++)a.push(arguments[i]);return dynCall.apply(null,a)}}');

// the UMD tail hoists its own empty `var Module`, so module arguments could never be passed in;
// read them from globalThis.__opencvModuleArgs instead (src/cv.js passes instantiateWasm there to
// initialise synchronously)
const tail = "  if (typeof Module === 'undefined')\n    var Module = {};\n  return cv(Module);";
if (!s.includes(tail)) throw new Error('not found: UMD tail');
s = s.replace(tail, "  return cv((typeof globalThis !== 'undefined' && globalThis.__opencvModuleArgs) || {});");

const left = (s.match(/new Function|new_\(Function/g) || []).length;
if (left) throw new Error(left + ' dynamic Function uses left');
fs.writeFileSync(out, s);
console.log('patched', inp, '->', out, s.length, 'bytes');
