const { readGray, writePNGgray, binaryToGray } = require('../src/image');
const { runOMR } = require('../src/pipeline');
const g = readGray(process.argv[2]);
const r = runOMR(g, {debug:true});
writePNGgray(process.argv[3], binaryToGray(r._debug.B));
writePNGgray(process.argv[4], binaryToGray(r._debug.R));
console.log(r.binarize);
