var globalThis = this;
var global = this;
function __skpm_run (key, context) {
  globalThis.context = context;
  try {

var exports =
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/my-command.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./node_modules/@babel/runtime/helpers/arrayLikeToArray.js":
/*!*****************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/arrayLikeToArray.js ***!
  \*****************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function _arrayLikeToArray(r, a) {
  (null == a || a > r.length) && (a = r.length);
  for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e];
  return n;
}
module.exports = _arrayLikeToArray, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/arrayWithoutHoles.js":
/*!******************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/arrayWithoutHoles.js ***!
  \******************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var arrayLikeToArray = __webpack_require__(/*! ./arrayLikeToArray.js */ "./node_modules/@babel/runtime/helpers/arrayLikeToArray.js");
function _arrayWithoutHoles(r) {
  if (Array.isArray(r)) return arrayLikeToArray(r);
}
module.exports = _arrayWithoutHoles, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/classCallCheck.js":
/*!***************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/classCallCheck.js ***!
  \***************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function _classCallCheck(a, n) {
  if (!(a instanceof n)) throw new TypeError("Cannot call a class as a function");
}
module.exports = _classCallCheck, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/createClass.js":
/*!************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/createClass.js ***!
  \************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var toPropertyKey = __webpack_require__(/*! ./toPropertyKey.js */ "./node_modules/@babel/runtime/helpers/toPropertyKey.js");
function _defineProperties(e, r) {
  for (var t = 0; t < r.length; t++) {
    var o = r[t];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, toPropertyKey(o.key), o);
  }
}
function _createClass(e, r, t) {
  return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
module.exports = _createClass, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/defineProperty.js":
/*!***************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/defineProperty.js ***!
  \***************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var toPropertyKey = __webpack_require__(/*! ./toPropertyKey.js */ "./node_modules/@babel/runtime/helpers/toPropertyKey.js");
function _defineProperty(e, r, t) {
  return (r = toPropertyKey(r)) in e ? Object.defineProperty(e, r, {
    value: t,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[r] = t, e;
}
module.exports = _defineProperty, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/iterableToArray.js":
/*!****************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/iterableToArray.js ***!
  \****************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function _iterableToArray(r) {
  if ("undefined" != typeof Symbol && null != r[Symbol.iterator] || null != r["@@iterator"]) return Array.from(r);
}
module.exports = _iterableToArray, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/nonIterableSpread.js":
/*!******************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/nonIterableSpread.js ***!
  \******************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function _nonIterableSpread() {
  throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
module.exports = _nonIterableSpread, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/toConsumableArray.js":
/*!******************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/toConsumableArray.js ***!
  \******************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var arrayWithoutHoles = __webpack_require__(/*! ./arrayWithoutHoles.js */ "./node_modules/@babel/runtime/helpers/arrayWithoutHoles.js");
var iterableToArray = __webpack_require__(/*! ./iterableToArray.js */ "./node_modules/@babel/runtime/helpers/iterableToArray.js");
var unsupportedIterableToArray = __webpack_require__(/*! ./unsupportedIterableToArray.js */ "./node_modules/@babel/runtime/helpers/unsupportedIterableToArray.js");
var nonIterableSpread = __webpack_require__(/*! ./nonIterableSpread.js */ "./node_modules/@babel/runtime/helpers/nonIterableSpread.js");
function _toConsumableArray(r) {
  return arrayWithoutHoles(r) || iterableToArray(r) || unsupportedIterableToArray(r) || nonIterableSpread();
}
module.exports = _toConsumableArray, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/toPrimitive.js":
/*!************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/toPrimitive.js ***!
  \************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var _typeof = __webpack_require__(/*! ./typeof.js */ "./node_modules/@babel/runtime/helpers/typeof.js")["default"];
function toPrimitive(t, r) {
  if ("object" != _typeof(t) || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != _typeof(i)) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
module.exports = toPrimitive, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/toPropertyKey.js":
/*!**************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/toPropertyKey.js ***!
  \**************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var _typeof = __webpack_require__(/*! ./typeof.js */ "./node_modules/@babel/runtime/helpers/typeof.js")["default"];
var toPrimitive = __webpack_require__(/*! ./toPrimitive.js */ "./node_modules/@babel/runtime/helpers/toPrimitive.js");
function toPropertyKey(t) {
  var i = toPrimitive(t, "string");
  return "symbol" == _typeof(i) ? i : i + "";
}
module.exports = toPropertyKey, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/typeof.js":
/*!*******************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/typeof.js ***!
  \*******************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function _typeof(o) {
  "@babel/helpers - typeof";

  return module.exports = _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) {
    return typeof o;
  } : function (o) {
    return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o;
  }, module.exports.__esModule = true, module.exports["default"] = module.exports, _typeof(o);
}
module.exports = _typeof, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/unsupportedIterableToArray.js":
/*!***************************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/unsupportedIterableToArray.js ***!
  \***************************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var arrayLikeToArray = __webpack_require__(/*! ./arrayLikeToArray.js */ "./node_modules/@babel/runtime/helpers/arrayLikeToArray.js");
function _unsupportedIterableToArray(r, a) {
  if (r) {
    if ("string" == typeof r) return arrayLikeToArray(r, a);
    var t = {}.toString.call(r).slice(8, -1);
    return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? arrayLikeToArray(r, a) : void 0;
  }
}
module.exports = _unsupportedIterableToArray, module.exports.__esModule = true, module.exports["default"] = module.exports;

/***/ }),

/***/ "./node_modules/@skpm/fs/index.js":
/*!****************************************!*\
  !*** ./node_modules/@skpm/fs/index.js ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

// TODO: async. Should probably be done with NSFileHandle and some notifications
// TODO: file descriptor. Needs to be done with NSFileHandle
var Buffer = __webpack_require__(/*! buffer */ "buffer").Buffer;
var utils = __webpack_require__(/*! ./utils */ "./node_modules/@skpm/fs/utils.js");
var parseStat = utils.parseStat;
var fsError = utils.fsError;
var fsErrorForPath = utils.fsErrorForPath;
var encodingFromOptions = utils.encodingFromOptions;
var NOT_IMPLEMENTED = utils.NOT_IMPLEMENTED;

module.exports.constants = {
  F_OK: 0,
  R_OK: 4,
  W_OK: 2,
  X_OK: 1,
};

module.exports.access = NOT_IMPLEMENTED("access");

module.exports.accessSync = function (path, mode) {
  mode = mode | 0;
  var fileManager = NSFileManager.defaultManager();

  switch (mode) {
    case 0:
      canAccess = module.exports.existsSync(path);
      break;
    case 1:
      canAccess = Boolean(Number(fileManager.isExecutableFileAtPath(path)));
      break;
    case 2:
      canAccess = Boolean(Number(fileManager.isWritableFileAtPath(path)));
      break;
    case 3:
      canAccess =
        Boolean(Number(fileManager.isExecutableFileAtPath(path))) &&
        Boolean(Number(fileManager.isWritableFileAtPath(path)));
      break;
    case 4:
      canAccess = Boolean(Number(fileManager.isReadableFileAtPath(path)));
      break;
    case 5:
      canAccess =
        Boolean(Number(fileManager.isReadableFileAtPath(path))) &&
        Boolean(Number(fileManager.isExecutableFileAtPath(path)));
      break;
    case 6:
      canAccess =
        Boolean(Number(fileManager.isReadableFileAtPath(path))) &&
        Boolean(Number(fileManager.isWritableFileAtPath(path)));
      break;
    case 7:
      canAccess =
        Boolean(Number(fileManager.isReadableFileAtPath(path))) &&
        Boolean(Number(fileManager.isWritableFileAtPath(path))) &&
        Boolean(Number(fileManager.isExecutableFileAtPath(path)));
      break;
  }

  if (!canAccess) {
    throw new Error("Can't access " + String(path));
  }
};

module.exports.appendFile = NOT_IMPLEMENTED("appendFile");

module.exports.appendFileSync = function (file, data, options) {
  if (!module.exports.existsSync(file)) {
    return module.exports.writeFileSync(file, data, options);
  }

  var handle = NSFileHandle.fileHandleForWritingAtPath(file);
  handle.seekToEndOfFile();

  var encoding = encodingFromOptions(options, "utf8");

  var nsdata = Buffer.from(
    data,
    encoding === "NSData" || encoding === "buffer" ? undefined : encoding
  ).toNSData();

  handle.writeData(nsdata);
};

module.exports.chmod = NOT_IMPLEMENTED("chmod");

module.exports.chmodSync = function (path, mode) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  fileManager.setAttributes_ofItemAtPath_error(
    {
      NSFilePosixPermissions: mode,
    },
    path,
    err
  );

  if (err.value() !== null) {
    throw fsErrorForPath(path, undefined, err.value());
  }
};

module.exports.chown = NOT_IMPLEMENTED("chown");
module.exports.chownSync = NOT_IMPLEMENTED("chownSync");

module.exports.close = NOT_IMPLEMENTED("close");
module.exports.closeSync = NOT_IMPLEMENTED("closeSync");

module.exports.copyFile = NOT_IMPLEMENTED("copyFile");

module.exports.copyFileSync = function (path, dest, flags) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  fileManager.copyItemAtPath_toPath_error(path, dest, err);

  if (err.value() !== null) {
    throw fsErrorForPath(path, false, err.value());
  }
};

module.exports.createReadStream = NOT_IMPLEMENTED("createReadStream");
module.exports.createWriteStream = NOT_IMPLEMENTED("createWriteStream");

module.exports.exists = NOT_IMPLEMENTED("exists");

module.exports.existsSync = function (path) {
  var fileManager = NSFileManager.defaultManager();
  return Boolean(Number(fileManager.fileExistsAtPath(path)));
};

module.exports.fchmod = NOT_IMPLEMENTED("fchmod");
module.exports.fchmodSync = NOT_IMPLEMENTED("fchmodSync");
module.exports.fchown = NOT_IMPLEMENTED("fchown");
module.exports.fchownSync = NOT_IMPLEMENTED("fchownSync");
module.exports.fdatasync = NOT_IMPLEMENTED("fdatasync");
module.exports.fdatasyncSync = NOT_IMPLEMENTED("fdatasyncSync");
module.exports.fstat = NOT_IMPLEMENTED("fstat");
module.exports.fstatSync = NOT_IMPLEMENTED("fstatSync");
module.exports.fsync = NOT_IMPLEMENTED("fsync");
module.exports.fsyncSync = NOT_IMPLEMENTED("fsyncSync");
module.exports.ftruncate = NOT_IMPLEMENTED("ftruncate");
module.exports.ftruncateSync = NOT_IMPLEMENTED("ftruncateSync");
module.exports.futimes = NOT_IMPLEMENTED("futimes");
module.exports.futimesSync = NOT_IMPLEMENTED("futimesSync");

module.exports.lchmod = NOT_IMPLEMENTED("lchmod");
module.exports.lchmodSync = NOT_IMPLEMENTED("lchmodSync");
module.exports.lchown = NOT_IMPLEMENTED("lchown");
module.exports.lchownSync = NOT_IMPLEMENTED("lchownSync");

module.exports.link = NOT_IMPLEMENTED("link");

module.exports.linkSync = function (existingPath, newPath) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  fileManager.linkItemAtPath_toPath_error(existingPath, newPath, err);

  if (err.value() !== null) {
    throw fsErrorForPath(existingPath, undefined, err.value());
  }
};

module.exports.lstat = NOT_IMPLEMENTED("lstat");

module.exports.lstatSync = function (path) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  var result = fileManager.attributesOfItemAtPath_error(path, err);

  if (err.value() !== null) {
    throw fsErrorForPath(path, undefined, err.value());
  }

  return parseStat(result);
};

module.exports.mkdir = NOT_IMPLEMENTED("mkdir");

module.exports.mkdirSync = function (path, options) {
  var mode = 0o777;
  var recursive = false;
  if (options && options.mode) {
    mode = options.mode;
  }
  if (options && options.recursive) {
    recursive = options.recursive;
  }
  if (typeof options === "number") {
    mode = options;
  }
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  fileManager.createDirectoryAtPath_withIntermediateDirectories_attributes_error(
    path,
    recursive,
    {
      NSFilePosixPermissions: mode,
    },
    err
  );

  if (err.value() !== null) {
    throw new Error(err.value());
  }
};

module.exports.mkdtemp = NOT_IMPLEMENTED("mkdtemp");

module.exports.mkdtempSync = function (path) {
  function makeid() {
    var text = "";
    var possible =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for (var i = 0; i < 6; i++)
      text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
  }
  var tempPath = path + makeid();
  module.exports.mkdirSync(tempPath);
  return tempPath;
};

module.exports.open = NOT_IMPLEMENTED("open");
module.exports.openSync = NOT_IMPLEMENTED("openSync");

module.exports.read = NOT_IMPLEMENTED("read");

module.exports.readdir = NOT_IMPLEMENTED("readdir");

module.exports.readdirSync = function (path, options) {
  var encoding = encodingFromOptions(options, "utf8");
  var fileManager = NSFileManager.defaultManager();
  var paths = fileManager.subpathsAtPath(path);
  var arr = [];
  for (var i = 0; i < paths.length; i++) {
    var pathName = paths[i];
    arr.push(encoding === "buffer" ? Buffer.from(pathName) : String(pathName));
  }
  return arr;
};

module.exports.readFile = NOT_IMPLEMENTED("readFile");

module.exports.readFileSync = function (path, options) {
  var encoding = encodingFromOptions(options, "buffer");
  var fileManager = NSFileManager.defaultManager();
  var data = fileManager.contentsAtPath(path);
  if (!data) {
    throw fsErrorForPath(path, false);
  }

  var buffer = Buffer.from(data);

  if (encoding === "buffer") {
    return buffer;
  } else if (encoding === "NSData") {
    return buffer.toNSData();
  } else {
    return buffer.toString(encoding);
  }
};

module.exports.readlink = NOT_IMPLEMENTED("readlink");

module.exports.readlinkSync = function (path) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  var result = fileManager.destinationOfSymbolicLinkAtPath_error(path, err);

  if (err.value() !== null) {
    throw fsErrorForPath(path, undefined, err.value());
  }

  return String(result);
};

module.exports.readSync = NOT_IMPLEMENTED("readSync");

module.exports.realpath = NOT_IMPLEMENTED("realpath");
module.exports.realpath.native = NOT_IMPLEMENTED("realpath.native");

module.exports.realpathSync = function (path) {
  return String(
    NSString.stringWithString(path).stringByResolvingSymlinksInPath()
  );
};

module.exports.realpathSync.native = NOT_IMPLEMENTED("realpathSync.native");

module.exports.rename = NOT_IMPLEMENTED("rename");

module.exports.renameSync = function (oldPath, newPath) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  fileManager.moveItemAtPath_toPath_error(oldPath, newPath, err);

  var error = err.value();

  if (error !== null) {
    // if there is already a file, we need to overwrite it
    if (
      String(error.domain()) === "NSCocoaErrorDomain" &&
      Number(error.code()) === 516
    ) {
      var err2 = MOPointer.alloc().init();
      fileManager.replaceItemAtURL_withItemAtURL_backupItemName_options_resultingItemURL_error(
        NSURL.fileURLWithPath(newPath),
        NSURL.fileURLWithPath(oldPath),
        null,
        NSFileManagerItemReplacementUsingNewMetadataOnly,
        null,
        err2
      );
      if (err2.value() !== null) {
        throw fsErrorForPath(oldPath, undefined, err2.value());
      }
    } else {
      throw fsErrorForPath(oldPath, undefined, error);
    }
  }
};

module.exports.rmdir = NOT_IMPLEMENTED("rmdir");

module.exports.rmdirSync = function (path) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  var isDirectory = module.exports.lstatSync(path).isDirectory();
  if (!isDirectory) {
    throw fsError("ENOTDIR", {
      path: path,
      syscall: "rmdir",
    });
  }
  fileManager.removeItemAtPath_error(path, err);

  if (err.value() !== null) {
    throw fsErrorForPath(path, true, err.value(), "rmdir");
  }
};

module.exports.stat = NOT_IMPLEMENTED("stat");

// the only difference with lstat is that we resolve symlinks
//
// > lstat() is identical to stat(), except that if pathname is a symbolic
// > link, then it returns information about the link itself, not the file
// > that it refers to.
// http://man7.org/linux/man-pages/man2/lstat.2.html
module.exports.statSync = function (path) {
  return module.exports.lstatSync(module.exports.realpathSync(path));
};

module.exports.symlink = NOT_IMPLEMENTED("symlink");

module.exports.symlinkSync = function (target, path) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  var result = fileManager.createSymbolicLinkAtPath_withDestinationPath_error(
    path,
    target,
    err
  );

  if (err.value() !== null) {
    throw new Error(err.value());
  }
};

module.exports.truncate = NOT_IMPLEMENTED("truncate");

module.exports.truncateSync = function (path, len) {
  var hFile = NSFileHandle.fileHandleForUpdatingAtPath(sFilePath);
  hFile.truncateFileAtOffset(len || 0);
  hFile.closeFile();
};

module.exports.unlink = NOT_IMPLEMENTED("unlink");

module.exports.unlinkSync = function (path) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  var isDirectory = module.exports.lstatSync(path).isDirectory();
  if (isDirectory) {
    throw fsError("EPERM", {
      path: path,
      syscall: "unlink",
    });
  }
  var result = fileManager.removeItemAtPath_error(path, err);

  if (err.value() !== null) {
    throw fsErrorForPath(path, false, err.value());
  }
};

module.exports.unwatchFile = NOT_IMPLEMENTED("unwatchFile");

module.exports.utimes = NOT_IMPLEMENTED("utimes");

module.exports.utimesSync = function (path, aTime, mTime) {
  var err = MOPointer.alloc().init();
  var fileManager = NSFileManager.defaultManager();
  var result = fileManager.setAttributes_ofItemAtPath_error(
    {
      NSFileModificationDate: aTime,
    },
    path,
    err
  );

  if (err.value() !== null) {
    throw fsErrorForPath(path, undefined, err.value());
  }
};

module.exports.watch = NOT_IMPLEMENTED("watch");
module.exports.watchFile = NOT_IMPLEMENTED("watchFile");

module.exports.write = NOT_IMPLEMENTED("write");

module.exports.writeFile = NOT_IMPLEMENTED("writeFile");

module.exports.writeFileSync = function (path, data, options) {
  var encoding = encodingFromOptions(options, "utf8");

  var nsdata = Buffer.from(
    data,
    encoding === "NSData" || encoding === "buffer" ? undefined : encoding
  ).toNSData();

  nsdata.writeToFile_atomically(path, true);
};

module.exports.writeSync = NOT_IMPLEMENTED("writeSync");


/***/ }),

/***/ "./node_modules/@skpm/fs/utils.js":
/*!****************************************!*\
  !*** ./node_modules/@skpm/fs/utils.js ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

module.exports.parseStat = function parseStat(result) {
  return {
    dev: String(result.NSFileDeviceIdentifier),
    // ino: 48064969, The file system specific "Inode" number for the file.
    mode: result.NSFileType | result.NSFilePosixPermissions,
    nlink: Number(result.NSFileReferenceCount),
    uid: String(result.NSFileOwnerAccountID),
    gid: String(result.NSFileGroupOwnerAccountID),
    // rdev: 0, A numeric device identifier if the file is considered "special".
    size: Number(result.NSFileSize),
    // blksize: 4096, The file system block size for i/o operations.
    // blocks: 8, The number of blocks allocated for this file.
    atimeMs:
      Number(result.NSFileModificationDate.timeIntervalSince1970()) * 1000,
    mtimeMs:
      Number(result.NSFileModificationDate.timeIntervalSince1970()) * 1000,
    ctimeMs:
      Number(result.NSFileModificationDate.timeIntervalSince1970()) * 1000,
    birthtimeMs:
      Number(result.NSFileCreationDate.timeIntervalSince1970()) * 1000,
    atime: new Date(
      Number(result.NSFileModificationDate.timeIntervalSince1970()) * 1000 + 0.5
    ), // the 0.5 comes from the node source. Not sure why it's added but in doubt...
    mtime: new Date(
      Number(result.NSFileModificationDate.timeIntervalSince1970()) * 1000 + 0.5
    ),
    ctime: new Date(
      Number(result.NSFileModificationDate.timeIntervalSince1970()) * 1000 + 0.5
    ),
    birthtime: new Date(
      Number(result.NSFileCreationDate.timeIntervalSince1970()) * 1000 + 0.5
    ),
    isBlockDevice: function () {
      return result.NSFileType === NSFileTypeBlockSpecial;
    },
    isCharacterDevice: function () {
      return result.NSFileType === NSFileTypeCharacterSpecial;
    },
    isDirectory: function () {
      return result.NSFileType === NSFileTypeDirectory;
    },
    isFIFO: function () {
      return false;
    },
    isFile: function () {
      return result.NSFileType === NSFileTypeRegular;
    },
    isSocket: function () {
      return result.NSFileType === NSFileTypeSocket;
    },
    isSymbolicLink: function () {
      return result.NSFileType === NSFileTypeSymbolicLink;
    },
  };
};

var ERRORS = {
  EPERM: {
    message: "operation not permitted",
    errno: -1,
  },
  ENOENT: {
    message: "no such file or directory",
    errno: -2,
  },
  EACCES: {
    message: "permission denied",
    errno: -13,
  },
  ENOTDIR: {
    message: "not a directory",
    errno: -20,
  },
  EISDIR: {
    message: "illegal operation on a directory",
    errno: -21,
  },
};

function fsError(code, options) {
  var error = new Error(
    code +
      ": " +
      ERRORS[code].message +
      ", " +
      (options.syscall || "") +
      (options.path ? " '" + options.path + "'" : "")
  );

  Object.keys(options).forEach(function (k) {
    error[k] = options[k];
  });

  error.code = code;
  error.errno = ERRORS[code].errno;

  return error;
}

module.exports.fsError = fsError;

module.exports.fsErrorForPath = function fsErrorForPath(
  path,
  shouldBeDir,
  err,
  syscall
) {
  var fileManager = NSFileManager.defaultManager();
  var doesExist = fileManager.fileExistsAtPath(path);
  if (!doesExist) {
    return fsError("ENOENT", {
      path: path,
      syscall: syscall || "open",
    });
  }
  var isReadable = fileManager.isReadableFileAtPath(path);
  if (!isReadable) {
    return fsError("EACCES", {
      path: path,
      syscall: syscall || "open",
    });
  }
  if (typeof shouldBeDir !== "undefined") {
    var isDirectory = __webpack_require__(/*! ./index */ "./node_modules/@skpm/fs/index.js").lstatSync(path).isDirectory();
    if (isDirectory && !shouldBeDir) {
      return fsError("EISDIR", {
        path: path,
        syscall: syscall || "read",
      });
    } else if (!isDirectory && shouldBeDir) {
      return fsError("ENOTDIR", {
        path: path,
        syscall: syscall || "read",
      });
    }
  }
  return new Error(err || "Unknown error while manipulating " + path);
};

module.exports.encodingFromOptions = function encodingFromOptions(
  options,
  defaultValue
) {
  return options && options.encoding
    ? String(options.encoding)
    : options
    ? String(options)
    : defaultValue;
};

module.exports.NOT_IMPLEMENTED = function NOT_IMPLEMENTED(name) {
  return function () {
    throw new Error(
      "fs." +
        name +
        " is not implemented yet. If you feel like implementing it, any contribution will be gladly accepted on https://github.com/skpm/fs"
    );
  };
};


/***/ }),

/***/ "./node_modules/@skpm/path/index.js":
/*!******************************************!*\
  !*** ./node_modules/@skpm/path/index.js ***!
  \******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

// Copyright Joyent, Inc. and other Node contributors.
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the
// "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish,
// distribute, sublicense, and/or sell copies of the Software, and to permit
// persons to whom the Software is furnished to do so, subject to the
// following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
// NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
// DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
// OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
// USE OR OTHER DEALINGS IN THE SOFTWARE.

var sketchSpecifics = __webpack_require__(/*! ./sketch-specifics */ "./node_modules/@skpm/path/sketch-specifics.js")

// we only expose the posix implementation since Sketch only runs on macOS

var CHAR_FORWARD_SLASH = 47
var CHAR_DOT = 46

// Resolves . and .. elements in a path with directory names
function normalizeString(path, allowAboveRoot) {
  var res = ''
  var lastSegmentLength = 0
  var lastSlash = -1
  var dots = 0
  var code
  for (var i = 0; i <= path.length; i += 1) {
    if (i < path.length) code = path.charCodeAt(i)
    else if (code === CHAR_FORWARD_SLASH) break
    else code = CHAR_FORWARD_SLASH
    if (code === CHAR_FORWARD_SLASH) {
      if (lastSlash === i - 1 || dots === 1) {
        // NOOP
      } else if (lastSlash !== i - 1 && dots === 2) {
        if (
          res.length < 2 ||
          lastSegmentLength !== 2 ||
          res.charCodeAt(res.length - 1) !== CHAR_DOT ||
          res.charCodeAt(res.length - 2) !== CHAR_DOT
        ) {
          if (res.length > 2) {
            var lastSlashIndex = res.lastIndexOf('/')
            if (lastSlashIndex !== res.length - 1) {
              if (lastSlashIndex === -1) {
                res = ''
                lastSegmentLength = 0
              } else {
                res = res.slice(0, lastSlashIndex)
                lastSegmentLength = res.length - 1 - res.lastIndexOf('/')
              }
              lastSlash = i
              dots = 0
              continue
            }
          } else if (res.length === 2 || res.length === 1) {
            res = ''
            lastSegmentLength = 0
            lastSlash = i
            dots = 0
            continue
          }
        }
        if (allowAboveRoot) {
          if (res.length > 0) res += '/..'
          else res = '..'
          lastSegmentLength = 2
        }
      } else {
        if (res.length > 0) res += '/' + path.slice(lastSlash + 1, i)
        else res = path.slice(lastSlash + 1, i)
        lastSegmentLength = i - lastSlash - 1
      }
      lastSlash = i
      dots = 0
    } else if (code === CHAR_DOT && dots !== -1) {
      ++dots
    } else {
      dots = -1
    }
  }
  return res
}

function _format(sep, pathObject) {
  var dir = pathObject.dir || pathObject.root
  var base =
    pathObject.base || (pathObject.name || '') + (pathObject.ext || '')
  if (!dir) {
    return base
  }
  if (dir === pathObject.root) {
    return dir + base
  }
  return dir + sep + base
}

var posix = {
  // path.resolve([from ...], to)
  resolve: function resolve() {
    var resolvedPath = ''
    var resolvedAbsolute = false
    var cwd

    for (var i = arguments.length - 1; i >= -1 && !resolvedAbsolute; i -= 1) {
      var path
      if (i >= 0) {
        path = arguments[i]
      } else {
        if (cwd === undefined) {
          cwd = posix.dirname(sketchSpecifics.cwd())
        }
        path = cwd
      }

      path = sketchSpecifics.getString(path, 'path')

      // Skip empty entries
      if (path.length === 0) {
        continue
      }

      resolvedPath = path + '/' + resolvedPath
      resolvedAbsolute = path.charCodeAt(0) === CHAR_FORWARD_SLASH
    }

    // At this point the path should be resolved to a full absolute path, but
    // handle relative paths to be safe (might happen when process.cwd() fails)

    // Normalize the path
    resolvedPath = normalizeString(resolvedPath, !resolvedAbsolute)

    if (resolvedAbsolute) {
      if (resolvedPath.length > 0) return '/' + resolvedPath
      else return '/'
    } else if (resolvedPath.length > 0) {
      return resolvedPath
    } else {
      return '.'
    }
  },

  normalize: function normalize(path) {
    path = sketchSpecifics.getString(path, 'path')

    if (path.length === 0) return '.'

    var isAbsolute = path.charCodeAt(0) === CHAR_FORWARD_SLASH
    var trailingSeparator =
      path.charCodeAt(path.length - 1) === CHAR_FORWARD_SLASH

    // Normalize the path
    path = normalizeString(path, !isAbsolute)

    if (path.length === 0 && !isAbsolute) path = '.'
    if (path.length > 0 && trailingSeparator) path += '/'

    if (isAbsolute) return '/' + path
    return path
  },

  isAbsolute: function isAbsolute(path) {
    path = sketchSpecifics.getString(path, 'path')
    return path.length > 0 && path.charCodeAt(0) === CHAR_FORWARD_SLASH
  },

  join: function join() {
    if (arguments.length === 0) return '.'
    var joined
    for (var i = 0; i < arguments.length; i += 1) {
      var arg = arguments[i]
      arg = sketchSpecifics.getString(arg, 'path')
      if (arg.length > 0) {
        if (joined === undefined) joined = arg
        else joined += '/' + arg
      }
    }
    if (joined === undefined) return '.'
    return posix.normalize(joined)
  },

  relative: function relative(from, to) {
    from = sketchSpecifics.getString(from, 'from path')
    to = sketchSpecifics.getString(to, 'to path')

    if (from === to) return ''

    from = posix.resolve(from)
    to = posix.resolve(to)

    if (from === to) return ''

    // Trim any leading backslashes
    var fromStart = 1
    for (; fromStart < from.length; fromStart += 1) {
      if (from.charCodeAt(fromStart) !== CHAR_FORWARD_SLASH) break
    }
    var fromEnd = from.length
    var fromLen = fromEnd - fromStart

    // Trim any leading backslashes
    var toStart = 1
    for (; toStart < to.length; toStart += 1) {
      if (to.charCodeAt(toStart) !== CHAR_FORWARD_SLASH) break
    }
    var toEnd = to.length
    var toLen = toEnd - toStart

    // Compare paths to find the longest common path from root
    var length = fromLen < toLen ? fromLen : toLen
    var lastCommonSep = -1
    var i = 0
    for (; i <= length; i += 1) {
      if (i === length) {
        if (toLen > length) {
          if (to.charCodeAt(toStart + i) === CHAR_FORWARD_SLASH) {
            // We get here if `from` is the exact base path for `to`.
            // For example: from='/foo/bar'; to='/foo/bar/baz'
            return to.slice(toStart + i + 1)
          } else if (i === 0) {
            // We get here if `from` is the root
            // For example: from='/'; to='/foo'
            return to.slice(toStart + i)
          }
        } else if (fromLen > length) {
          if (from.charCodeAt(fromStart + i) === CHAR_FORWARD_SLASH) {
            // We get here if `to` is the exact base path for `from`.
            // For example: from='/foo/bar/baz'; to='/foo/bar'
            lastCommonSep = i
          } else if (i === 0) {
            // We get here if `to` is the root.
            // For example: from='/foo'; to='/'
            lastCommonSep = 0
          }
        }
        break
      }
      var fromCode = from.charCodeAt(fromStart + i)
      var toCode = to.charCodeAt(toStart + i)
      if (fromCode !== toCode) break
      else if (fromCode === CHAR_FORWARD_SLASH) lastCommonSep = i
    }

    var out = ''
    // Generate the relative path based on the path difference between `to`
    // and `from`
    for (i = fromStart + lastCommonSep + 1; i <= fromEnd; i += 1) {
      if (i === fromEnd || from.charCodeAt(i) === CHAR_FORWARD_SLASH) {
        if (out.length === 0) out += '..'
        else out += '/..'
      }
    }

    // Lastly, append the rest of the destination (`to`) path that comes after
    // the common path parts
    if (out.length > 0) return out + to.slice(toStart + lastCommonSep)
    else {
      toStart += lastCommonSep
      if (to.charCodeAt(toStart) === CHAR_FORWARD_SLASH) toStart += 1
      return to.slice(toStart)
    }
  },

  toNamespacedPath: function toNamespacedPath(path) {
    // Non-op on posix systems
    return path
  },

  dirname: function dirname(path) {
    path = sketchSpecifics.getString(path, 'path')
    if (path.length === 0) return '.'
    var code = path.charCodeAt(0)
    var hasRoot = code === CHAR_FORWARD_SLASH
    var end = -1
    var matchedSlash = true
    for (var i = path.length - 1; i >= 1; i -= 1) {
      code = path.charCodeAt(i)
      if (code === CHAR_FORWARD_SLASH) {
        if (!matchedSlash) {
          end = i
          break
        }
      } else {
        // We saw the first non-path separator
        matchedSlash = false
      }
    }

    if (end === -1) return hasRoot ? '/' : '.'
    if (hasRoot && end === 1) return '//'
    return path.slice(0, end)
  },

  basename: function basename(path, ext) {
    if (ext !== undefined)
      ext = sketchSpecifics.getString(ext, 'ext')
    path = sketchSpecifics.getString(path, 'path')

    var start = 0
    var end = -1
    var matchedSlash = true
    var i

    if (ext !== undefined && ext.length > 0 && ext.length <= path.length) {
      if (ext.length === path.length && ext === path) return ''
      var extIdx = ext.length - 1
      var firstNonSlashEnd = -1
      for (i = path.length - 1; i >= 0; i -= 1) {
        var code = path.charCodeAt(i)
        if (code === CHAR_FORWARD_SLASH) {
          // If we reached a path separator that was not part of a set of path
          // separators at the end of the string, stop now
          if (!matchedSlash) {
            start = i + 1
            break
          }
        } else {
          if (firstNonSlashEnd === -1) {
            // We saw the first non-path separator, remember this index in case
            // we need it if the extension ends up not matching
            matchedSlash = false
            firstNonSlashEnd = i + 1
          }
          if (extIdx >= 0) {
            // Try to match the explicit extension
            if (code === ext.charCodeAt(extIdx)) {
              if (--extIdx === -1) {
                // We matched the extension, so mark this as the end of our path
                // component
                end = i
              }
            } else {
              // Extension does not match, so our result is the entire path
              // component
              extIdx = -1
              end = firstNonSlashEnd
            }
          }
        }
      }

      if (start === end) end = firstNonSlashEnd
      else if (end === -1) end = path.length
      return path.slice(start, end)
    } else {
      for (i = path.length - 1; i >= 0; --i) {
        if (path.charCodeAt(i) === CHAR_FORWARD_SLASH) {
          // If we reached a path separator that was not part of a set of path
          // separators at the end of the string, stop now
          if (!matchedSlash) {
            start = i + 1
            break
          }
        } else if (end === -1) {
          // We saw the first non-path separator, mark this as the end of our
          // path component
          matchedSlash = false
          end = i + 1
        }
      }

      if (end === -1) return ''
      return path.slice(start, end)
    }
  },

  extname: function extname(path) {
    path = sketchSpecifics.getString(path, 'path')
    var startDot = -1
    var startPart = 0
    var end = -1
    var matchedSlash = true
    // Track the state of characters (if any) we see before our first dot and
    // after any path separator we find
    var preDotState = 0
    for (var i = path.length - 1; i >= 0; --i) {
      var code = path.charCodeAt(i)
      if (code === CHAR_FORWARD_SLASH) {
        // If we reached a path separator that was not part of a set of path
        // separators at the end of the string, stop now
        if (!matchedSlash) {
          startPart = i + 1
          break
        }
        continue
      }
      if (end === -1) {
        // We saw the first non-path separator, mark this as the end of our
        // extension
        matchedSlash = false
        end = i + 1
      }
      if (code === CHAR_DOT) {
        // If this is our first dot, mark it as the start of our extension
        if (startDot === -1) startDot = i
        else if (preDotState !== 1) preDotState = 1
      } else if (startDot !== -1) {
        // We saw a non-dot and non-path separator before our dot, so we should
        // have a good chance at having a non-empty extension
        preDotState = -1
      }
    }

    if (
      startDot === -1 ||
      end === -1 ||
      // We saw a non-dot character immediately before the dot
      preDotState === 0 ||
      // The (right-most) trimmed path component is exactly '..'
      (preDotState === 1 && startDot === end - 1 && startDot === startPart + 1)
    ) {
      return ''
    }
    return path.slice(startDot, end)
  },

  format: function format(pathObject) {
    if (pathObject === null || typeof pathObject !== 'object') {
      throw new Error('pathObject should be an Object')
    }
    return _format('/', pathObject)
  },

  parse: function parse(path) {
    path = sketchSpecifics.getString(path, 'path')

    var ret = { root: '', dir: '', base: '', ext: '', name: '' }
    if (path.length === 0) return ret
    var code = path.charCodeAt(0)
    var isAbsolute = code === CHAR_FORWARD_SLASH
    var start
    if (isAbsolute) {
      ret.root = '/'
      start = 1
    } else {
      start = 0
    }
    var startDot = -1
    var startPart = 0
    var end = -1
    var matchedSlash = true
    var i = path.length - 1

    // Track the state of characters (if any) we see before our first dot and
    // after any path separator we find
    var preDotState = 0

    // Get non-dir info
    for (; i >= start; --i) {
      code = path.charCodeAt(i)
      if (code === CHAR_FORWARD_SLASH) {
        // If we reached a path separator that was not part of a set of path
        // separators at the end of the string, stop now
        if (!matchedSlash) {
          startPart = i + 1
          break
        }
        continue
      }
      if (end === -1) {
        // We saw the first non-path separator, mark this as the end of our
        // extension
        matchedSlash = false
        end = i + 1
      }
      if (code === CHAR_DOT) {
        // If this is our first dot, mark it as the start of our extension
        if (startDot === -1) startDot = i
        else if (preDotState !== 1) preDotState = 1
      } else if (startDot !== -1) {
        // We saw a non-dot and non-path separator before our dot, so we should
        // have a good chance at having a non-empty extension
        preDotState = -1
      }
    }

    if (
      startDot === -1 ||
      end === -1 ||
      // We saw a non-dot character immediately before the dot
      preDotState === 0 ||
      // The (right-most) trimmed path component is exactly '..'
      (preDotState === 1 && startDot === end - 1 && startDot === startPart + 1)
    ) {
      if (end !== -1) {
        if (startPart === 0 && isAbsolute)
          ret.base = ret.name = path.slice(1, end)
        else ret.base = ret.name = path.slice(startPart, end)
      }
    } else {
      if (startPart === 0 && isAbsolute) {
        ret.name = path.slice(1, startDot)
        ret.base = path.slice(1, end)
      } else {
        ret.name = path.slice(startPart, startDot)
        ret.base = path.slice(startPart, end)
      }
      ret.ext = path.slice(startDot, end)
    }

    if (startPart > 0) ret.dir = path.slice(0, startPart - 1)
    else if (isAbsolute) ret.dir = '/'

    return ret
  },

  sep: '/',
  delimiter: ':',
  win32: null,
  posix: null,

  resourcePath: sketchSpecifics.resourcePath,
}

module.exports = posix
module.exports.posix = posix


/***/ }),

/***/ "./node_modules/@skpm/path/sketch-specifics.js":
/*!*****************************************************!*\
  !*** ./node_modules/@skpm/path/sketch-specifics.js ***!
  \*****************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var util = __webpack_require__(/*! util */ "util")

module.exports.getString = function getString(path, argumentName) {
  if (!util.isString(path)) {
    // let's make a special case for NSURL
    if (util.getNativeClass(path) === 'NSURL') {
      return String(path.path().copy())
    }
    throw new Error(argumentName + ' should be a string. Got ' + typeof path + ' instead.')
  }
  return String(path)
}

module.exports.cwd = function cwd() {
  if (typeof __command !== 'undefined' && __command.script() && __command.script().URL()) {
    return String(__command.script().URL().path().copy())
  }
  return String(MSPluginManager.defaultPluginURL().path().copy())
}

module.exports.resourcePath = function resourcePath(resourceName) {
  if (typeof __command === 'undefined' || !__command.pluginBundle()) {
    return undefined
  }
  var resource = __command.pluginBundle().urlForResourceNamed(resourceName)
  if (!resource) {
    return undefined
  }
  return String(resource.path())
}


/***/ }),

/***/ "./src/my-command.js":
/*!***************************!*\
  !*** ./src/my-command.js ***!
  \***************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var sketch__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! sketch */ "sketch");
/* harmony import */ var sketch__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(sketch__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _styleTree_generateStyleTree__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./styleTree/generateStyleTree */ "./src/styleTree/generateStyleTree.js");
/* harmony import */ var _skpm_fs__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @skpm/fs */ "./node_modules/@skpm/fs/index.js");
/* harmony import */ var _skpm_fs__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_skpm_fs__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _skpm_path__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @skpm/path */ "./node_modules/@skpm/path/index.js");
/* harmony import */ var _skpm_path__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_skpm_path__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _originalStyles__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./originalStyles */ "./src/originalStyles/index.js");
/* harmony import */ var _sketchToCss_bordersToCss__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./sketchToCss/bordersToCss */ "./src/sketchToCss/bordersToCss.js");
/* harmony import */ var _sketchToCss_test__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./sketchToCss/test */ "./src/sketchToCss/test.js");

// documentation: https://developer.sketchapp.com/reference/api/






/* harmony default export */ __webpack_exports__["default"] = (function () {
  /* const document = sketch.getSelectedDocument()
  const page = document.pages[0];
  const login = page.layers[0]
   console.log(login);
  
  
  
  const styleTree = generateStyleTree(login)
   // 导出到插件根目录
  const filePath = path.join(process.cwd(), 'styleTree.json')
  fs.writeFileSync(filePath, JSON.stringify(styleTree, null, 2), 'utf8') 
  sketch.UI.message('样式树已导出到插件目录 styleTree.json')
  */

  // 处理原始样式（所有逻辑都在 originalStyles 中完成）

  // processOriginalStyles(sketch, fs, path)
  Object(_sketchToCss_test__WEBPACK_IMPORTED_MODULE_6__["default"])();
  console.log('end');
});

/***/ }),

/***/ "./src/originalStyles/exportStyles.js":
/*!********************************************!*\
  !*** ./src/originalStyles/exportStyles.js ***!
  \********************************************/
/*! exports provided: exportOriginalStyles, exportStylesToClipboard, getStylesStatistics */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "exportOriginalStyles", function() { return exportOriginalStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "exportStylesToClipboard", function() { return exportStylesToClipboard; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getStylesStatistics", function() { return getStylesStatistics; });
/* harmony import */ var _getOriginalStyles__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./getOriginalStyles */ "./src/originalStyles/getOriginalStyles.js");


/**
 * 导出原始样式为JSON文件
 * @param {Object} context - Sketch 上下文对象
 * @param {Object} options - 导出选项
 * @returns {Object} 导出结果
 */
var exportOriginalStyles = function exportOriginalStyles(context) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  // 获取原始样式数据
  var stylesData = Object(_getOriginalStyles__WEBPACK_IMPORTED_MODULE_0__["getSelectedLayerOriginalStyles"])(context);
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }

  // 构建导出文件名
  var timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  var layerName = stylesData.container ? stylesData.container.name.replace(/[^a-zA-Z0-9]/g, '_') : 'unknown_layer';
  var fileName = "original_styles_".concat(layerName, "_").concat(timestamp, ".json");

  // 构建完整的导出数据
  var exportData = {
    metadata: {
      exportType: 'original_styles',
      // sketchVersion: context.api.version,
      exportTime: new Date().toISOString(),
      fileName: fileName,
      options: options
    },
    styles: stylesData
  };

  // 格式化JSON字符串
  var jsonString = JSON.stringify(exportData, null, 2);

  // 创建文件内容
  var fileContent = jsonString;

  // 计算总图层数量（递归统计）
  var _countLayers = function countLayers(node) {
    var count = 1; // 当前节点
    if (node.children && node.children.length > 0) {
      node.children.forEach(function (child) {
        count += _countLayers(child);
      });
    }
    return count;
  };
  var totalLayers = _countLayers(stylesData);

  // 返回导出结果
  return {
    success: true,
    fileName: fileName,
    fileContent: fileContent,
    dataSize: fileContent.length,
    layerCount: totalLayers,
    timestamp: new Date().toISOString()
  };
};

/**
 * 导出样式数据到剪贴板
 * @param {Object} context - Sketch 上下文对象
 * @returns {Object} 导出结果
 */
var exportStylesToClipboard = function exportStylesToClipboard(context) {
  var stylesData = Object(_getOriginalStyles__WEBPACK_IMPORTED_MODULE_0__["getSelectedLayerOriginalStyles"])(context);
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }

  // 格式化JSON字符串
  var jsonString = JSON.stringify(stylesData, null, 2);

  // 复制到剪贴板（需要Sketch API支持）
  if (context.api && context.api.copyToClipboard) {
    context.api.copyToClipboard(jsonString);
  }
  return {
    success: true,
    message: '样式数据已复制到剪贴板',
    dataSize: jsonString.length
  };
};

/**
 * 获取样式数据的统计信息
 * @param {Object} context - Sketch 上下文对象
 * @returns {Object} 统计信息
 */
var getStylesStatistics = function getStylesStatistics(context) {
  var stylesData = Object(_getOriginalStyles__WEBPACK_IMPORTED_MODULE_0__["getSelectedLayerOriginalStyles"])(context);
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }
  var stats = {
    success: true,
    containerName: stylesData.container ? stylesData.container.name : 'N/A',
    containerType: stylesData.container ? stylesData.container.type : 'N/A',
    totalLayers: stylesData.metadata ? stylesData.metadata.totalLayers : 1,
    layerTypes: stylesData.metadata ? stylesData.metadata.layerTypes : {},
    hasFills: false,
    hasBorders: false,
    hasShadows: false,
    hasTextStyles: false,
    timestamp: new Date().toISOString()
  };

  // 分析样式类型
  var analyzeLayerStyles = function analyzeLayerStyles(layer) {
    if (layer.style) {
      if (layer.style.fills && layer.style.fills.length > 0) stats.hasFills = true;
      if (layer.style.borders && layer.style.borders.length > 0) stats.hasBorders = true;
      if (layer.style.shadows && layer.style.shadows.length > 0) stats.hasShadows = true;
      if (layer.style.textStyle) stats.hasTextStyles = true;
    }
  };

  // 分析容器样式
  if (stylesData.container) {
    analyzeLayerStyles(stylesData.container);
  }

  // 分析子图层样式
  if (stylesData.children) {
    stylesData.children.forEach(function (child) {
      analyzeLayerStyles(child);
    });
  }
  return stats;
};


/***/ }),

/***/ "./src/originalStyles/getOriginalStyles.js":
/*!*************************************************!*\
  !*** ./src/originalStyles/getOriginalStyles.js ***!
  \*************************************************/
/*! exports provided: getLayerOriginalStyles, getContainerOriginalStyles, getSelectedLayerOriginalStyles, debugPrintLayerStructure */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getLayerOriginalStyles", function() { return getLayerOriginalStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getContainerOriginalStyles", function() { return _getContainerOriginalStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getSelectedLayerOriginalStyles", function() { return getSelectedLayerOriginalStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "debugPrintLayerStructure", function() { return _debugPrintLayerStructure; });
/* harmony import */ var _skpm_path__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @skpm/path */ "./node_modules/@skpm/path/index.js");
/* harmony import */ var _skpm_path__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_skpm_path__WEBPACK_IMPORTED_MODULE_0__);
/**
 * 获取图层的原始样式属性
 * @param {Object} layer - Sketch 图层对象
 * @returns {Object} 包含所有原始样式属性的对象
 */

var getLayerOriginalStyles = function getLayerOriginalStyles(layer) {
  if (!layer) {
    return null;
  }
  var styles = {
    // 基本信息
    id: layer.id,
    name: layer.name,
    type: layer.type,
    // 位置和尺寸
    frame: layer.frame ? {
      x: layer.frame.x,
      y: layer.frame.y,
      width: layer.frame.width,
      height: layer.frame.height
    } : null,
    // 变换属性
    transform: layer.transform ? {
      rotation: layer.transform.rotation,
      flippedHorizontally: layer.transform.flippedHorizontally,
      flippedVertically: layer.transform.flippedVertically
    } : null,
    // 样式属性
    style: {}
  };
  console.log(layer.name);
  if (layer.name === '矩形') {
    console.log('====================', layer.name);
    console.log(JSON.stringify(layer));
    console.log('====================', layer.name);
  }

  // 填充样式
  if (layer.style && layer.style.fills) {
    styles.style.fills = layer.style.fills.map(function (fill) {
      return {
        fillType: fill.fillType,
        color: fill.color ? {
          red: fill.color.red,
          green: fill.color.green,
          blue: fill.color.blue,
          alpha: fill.color.alpha
        } : null,
        gradient: fill.gradient,
        pattern: fill.pattern,
        noiseIndex: fill.noiseIndex,
        noiseIntensity: fill.noiseIntensity,
        isEnabled: fill.isEnabled
      };
    });
  }

  // 边框样式
  if (layer.style && layer.style.borders) {
    styles.style.borders = layer.style.borders.map(function (border) {
      return {
        fillType: border.fillType,
        color: border.color ? {
          red: border.color.red,
          green: border.color.green,
          blue: border.color.blue,
          alpha: border.color.alpha
        } : null,
        thickness: border.thickness,
        position: border.position,
        isEnabled: border.isEnabled
      };
    });
  }

  // 阴影样式
  if (layer.style && layer.style.shadows) {
    styles.style.shadows = layer.style.shadows.map(function (shadow) {
      return {
        color: shadow.color ? {
          red: shadow.color.red,
          green: shadow.color.green,
          blue: shadow.color.blue,
          alpha: shadow.color.alpha
        } : null,
        offsetX: shadow.offsetX,
        offsetY: shadow.offsetY,
        blurRadius: shadow.blurRadius,
        spread: shadow.spread,
        isEnabled: shadow.isEnabled
      };
    });
  }

  // 内阴影样式
  if (layer.style && layer.style.innerShadows) {
    styles.style.innerShadows = layer.style.innerShadows.map(function (shadow) {
      return {
        color: shadow.color ? {
          red: shadow.color.red,
          green: shadow.color.green,
          blue: shadow.color.blue,
          alpha: shadow.color.alpha
        } : null,
        offsetX: shadow.offsetX,
        offsetY: shadow.offsetY,
        blurRadius: shadow.blurRadius,
        spread: shadow.spread,
        isEnabled: shadow.isEnabled
      };
    });
  }

  // 文本样式（仅对文本图层）
  if (layer.type === 'Text' && layer.style && layer.style.textStyle) {
    styles.style.textStyle = {
      fontName: layer.style.textStyle.fontName,
      fontSize: layer.style.textStyle.fontSize,
      lineHeight: layer.style.textStyle.lineHeight,
      letterSpacing: layer.style.textStyle.letterSpacing,
      textAlign: layer.style.textStyle.textAlign,
      color: layer.style.textStyle.color ? {
        red: layer.style.textStyle.color.red,
        green: layer.style.textStyle.color.green,
        blue: layer.style.textStyle.color.blue,
        alpha: layer.style.textStyle.color.alpha
      } : null
    };
  }

  // 模糊效果
  if (layer.style && layer.style.blur) {
    styles.style.blur = {
      type: layer.style.blur.type,
      radius: layer.style.blur.radius,
      center: layer.style.blur.center,
      motionAngle: layer.style.blur.motionAngle,
      isEnabled: layer.style.blur.isEnabled
    };
  }

  // 混合模式
  if (layer.style && layer.style.blendMode) {
    styles.style.blendMode = layer.style.blendMode;
  }

  // 透明度
  if (layer.style && layer.style.opacity !== undefined) {
    styles.style.opacity = layer.style.opacity;
  }
  return styles;
};

/**
 * 递归获取容器及其所有子元素的原始样式
 * @param {Object} container - 容器图层（编组或框架）
 * @returns {Object} 包含容器和所有子元素样式的对象
 */
var _getContainerOriginalStyles = function getContainerOriginalStyles(container) {
  if (!container) {
    return null;
  }
  console.log(1);
  var result = {
    id: container.id,
    name: container.name,
    type: container.type,
    frame: container.frame ? {
      x: container.frame.x,
      y: container.frame.y,
      width: container.frame.width,
      height: container.frame.height
    } : null,
    style: getLayerOriginalStyles(container).style,
    children: [],
    metadata: {
      totalLayers: 0,
      layerTypes: {},
      timestamp: new Date().toISOString()
    }
  };
  console.log(2);
  // 递归处理子图层
  if (container.layers && container.layers.length > 0) {
    result.children = container.layers.map(function (child) {
      // 统计图层类型
      if (child.type) {
        result.metadata.layerTypes[child.type] = (result.metadata.layerTypes[child.type] || 0) + 1;
      }
      result.metadata.totalLayers++;

      // 递归处理子元素：如果子元素也是容器，则递归获取其子元素
      if (child.type === 'Group' || child.type === 'Artboard') {
        return _getContainerOriginalStyles(child);
      } else {
        // 叶子节点：返回完整的图层信息
        return {
          id: child.id,
          name: child.name,
          type: child.type,
          frame: child.frame ? {
            x: child.frame.x,
            y: child.frame.y,
            width: child.frame.width,
            height: child.frame.height
          } : null,
          style: getLayerOriginalStyles(child).style,
          children: [] // 叶子节点没有子元素
        };
      }
    });
  }
  return result;
};

/**
 * 获取当前选中图层的原始样式（JSON格式）
 * @param {Object} context - Sketch 上下文对象
 * @returns {Object} 包含原始样式的JSON对象
 */
var getSelectedLayerOriginalStyles = function getSelectedLayerOriginalStyles(context) {
  var selectedLayers = context.selection;
  if (!selectedLayers || selectedLayers.length === 0) {
    throw new Error('没有选中的图层');
  }

  // 使用 forEach 获取第一个选中的图层
  var clickedLayer = null;
  selectedLayers.forEach(function (layer) {
    if (!clickedLayer) {
      clickedLayer = layer;
    }
  });

  // 检查第一个元素是否存在
  if (!clickedLayer) {
    throw new Error('选中的图层无效或为空');
  }

  // 检查是否为容器类型
  if (clickedLayer.type === 'Group' || clickedLayer.type === 'Artboard') {
    return _getContainerOriginalStyles(clickedLayer);
  }

  // 如果不是容器，查找父级容器
  var parentLayer = clickedLayer.parent;
  while (parentLayer) {
    if (parentLayer.type === 'Group' || parentLayer.type === 'Artboard') {
      return _getContainerOriginalStyles(parentLayer);
    }
    parentLayer = parentLayer.parent;
  }

  // 如果都没有找到容器，返回单个图层的样式（也支持递归）
  return {
    id: clickedLayer.id,
    name: clickedLayer.name,
    type: clickedLayer.type,
    frame: clickedLayer.frame ? {
      x: clickedLayer.frame.x,
      y: clickedLayer.frame.y,
      width: clickedLayer.frame.width,
      height: clickedLayer.frame.height
    } : null,
    style: getLayerOriginalStyles(clickedLayer).style,
    children: clickedLayer.layers && clickedLayer.layers.length > 0 ? clickedLayer.layers.map(function (child) {
      if (child.type === 'Group' || child.type === 'Artboard') {
        return _getContainerOriginalStyles(child);
      } else {
        return {
          id: child.id,
          name: child.name,
          type: child.type,
          frame: child.frame ? {
            x: child.frame.x,
            y: child.frame.y,
            width: child.frame.width,
            height: child.frame.height
          } : null,
          style: getLayerOriginalStyles(child).style,
          children: []
        };
      }
    }) : [],
    note: '单个图层样式',
    timestamp: new Date().toISOString()
  };
};

/**
 * 递归打印图层结构（用于调试）
 * @param {Object} node - 图层节点
 * @param {number} depth - 当前深度
 */
var _debugPrintLayerStructure = function debugPrintLayerStructure(node) {
  var depth = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;
  var indent = '  '.repeat(depth);
  console.log("".concat(indent).concat(node.type, ": ").concat(node.name, " (").concat(node.children ? node.children.length : 0, " children)"));
  if (node.children && node.children.length > 0) {
    node.children.forEach(function (child) {
      _debugPrintLayerStructure(child, depth + 1);
    });
  }
};


/***/ }),

/***/ "./src/originalStyles/index.js":
/*!*************************************!*\
  !*** ./src/originalStyles/index.js ***!
  \*************************************/
/*! exports provided: getAndExportOriginalStyles, quickGetOriginalStyles, quickExportStyles, validateLayerSelection, getStylesStats, exportStylesToClipboardFunc, processOriginalStyles, OriginalStylesManager, createOriginalStylesManager, getSelectedLayerOriginalStyles, exportOriginalStyles, exportStylesToClipboard, getStylesStatistics */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getAndExportOriginalStyles", function() { return getAndExportOriginalStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "quickGetOriginalStyles", function() { return quickGetOriginalStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "quickExportStyles", function() { return quickExportStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "validateLayerSelection", function() { return validateLayerSelection; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getStylesStats", function() { return getStylesStats; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "exportStylesToClipboardFunc", function() { return exportStylesToClipboardFunc; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "processOriginalStyles", function() { return processOriginalStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "OriginalStylesManager", function() { return OriginalStylesManager; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "createOriginalStylesManager", function() { return createOriginalStylesManager; });
/* harmony import */ var _babel_runtime_helpers_classCallCheck__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/classCallCheck */ "./node_modules/@babel/runtime/helpers/classCallCheck.js");
/* harmony import */ var _babel_runtime_helpers_classCallCheck__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_helpers_classCallCheck__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _babel_runtime_helpers_createClass__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/helpers/createClass */ "./node_modules/@babel/runtime/helpers/createClass.js");
/* harmony import */ var _babel_runtime_helpers_createClass__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_helpers_createClass__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @babel/runtime/helpers/defineProperty */ "./node_modules/@babel/runtime/helpers/defineProperty.js");
/* harmony import */ var _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _getOriginalStyles__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./getOriginalStyles */ "./src/originalStyles/getOriginalStyles.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "getSelectedLayerOriginalStyles", function() { return _getOriginalStyles__WEBPACK_IMPORTED_MODULE_3__["getSelectedLayerOriginalStyles"]; });

/* harmony import */ var _exportStyles__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./exportStyles */ "./src/originalStyles/exportStyles.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "exportOriginalStyles", function() { return _exportStyles__WEBPACK_IMPORTED_MODULE_4__["exportOriginalStyles"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "exportStylesToClipboard", function() { return _exportStyles__WEBPACK_IMPORTED_MODULE_4__["exportStylesToClipboard"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "getStylesStatistics", function() { return _exportStyles__WEBPACK_IMPORTED_MODULE_4__["getStylesStatistics"]; });




function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach(function (r) { _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_2___default()(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }



/**
 * 一键获取并导出原始样式（完整流程）
 * 包含选择验证、样式获取、文件导出等完整逻辑
 * @param {Object} sketchContext - Sketch 上下文对象
 * @param {Object} options - 导出选项
 * @returns {Object} 完整的结果对象
 */
var getAndExportOriginalStyles = function getAndExportOriginalStyles(sketchContext) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  // 1. 验证选择
  var validation = validateLayerSelection(sketchContext);
  if (!validation.valid) {
    throw new Error(validation.message);
  }

  // 2. 获取原始样式
  var stylesData = Object(_getOriginalStyles__WEBPACK_IMPORTED_MODULE_3__["getSelectedLayerOriginalStyles"])(sketchContext);
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }

  // 3. 导出样式
  var exportResult = Object(_exportStyles__WEBPACK_IMPORTED_MODULE_4__["exportOriginalStyles"])(sketchContext, _objectSpread({
    includeMetadata: true,
    format: 'pretty'
  }, options));
  if (!exportResult.success) {
    throw new Error(exportResult.error);
  }

  // 4. 返回完整结果
  return {
    success: true,
    validation: validation,
    stylesData: stylesData,
    exportResult: exportResult,
    statistics: {
      layerCount: exportResult.layerCount,
      dataSize: exportResult.dataSize,
      fileName: exportResult.fileName,
      containerName: stylesData.name || 'N/A',
      containerType: stylesData.type || 'N/A'
    }
  };
};

/**
 * 验证图层选择是否有效
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 验证结果
 */
var validateLayerSelection = function validateLayerSelection(sketchContext) {
  var selectedLayers = sketchContext.selection;
  if (!selectedLayers || selectedLayers.length === 0) {
    return {
      valid: false,
      message: '没有选中的图层'
    };
  }

  // 使用 forEach 获取第一个选中的图层
  var firstLayer = null;
  selectedLayers.forEach(function (layer) {
    if (!firstLayer) {
      firstLayer = layer;
    }
  });
  if (!firstLayer) {
    return {
      valid: false,
      message: '选中的图层无效或为空'
    };
  }
  var isContainer = firstLayer.type === 'Group' || firstLayer.type === 'Artboard';
  if (isContainer) {
    return {
      valid: true,
      message: "\u9009\u4E2D\u4E86".concat(firstLayer.type, "\u7C7B\u578B\u7684\u5BB9\u5668: ").concat(firstLayer.name),
      layerType: firstLayer.type,
      layerName: firstLayer.name
    };
  }

  // 检查是否有父级容器
  var parent = firstLayer.parent;
  while (parent) {
    if (parent.type === 'Group' || parent.type === 'Artboard') {
      return {
        valid: true,
        message: "\u9009\u4E2D\u4E86".concat(parent.type, "\u7C7B\u578B\u7684\u7236\u7EA7\u5BB9\u5668: ").concat(parent.name),
        layerType: parent.type,
        layerName: parent.name,
        selectedLayer: firstLayer.name
      };
    }
    parent = parent.parent;
  }
  return {
    valid: false,
    message: '选中的图层不在任何编组或框架内'
  };
};

/**
 * 快速获取原始样式（仅获取，不导出）
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 样式数据或错误信息
 */
var quickGetOriginalStyles = function quickGetOriginalStyles(sketchContext) {
  var validation = validateLayerSelection(sketchContext);
  if (!validation.valid) {
    throw new Error(validation.message);
  }
  var stylesData = Object(_getOriginalStyles__WEBPACK_IMPORTED_MODULE_3__["getSelectedLayerOriginalStyles"])(sketchContext);
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }
  return {
    success: true,
    data: stylesData,
    validation: validation
  };
};

/**
 * 快速导出样式（仅导出，不验证）
 * @param {Object} sketchContext - Sketch 上下文对象
 * @param {Object} options - 导出选项
 * @returns {Object} 导出结果
 */
var quickExportStyles = function quickExportStyles(sketchContext) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  return Object(_exportStyles__WEBPACK_IMPORTED_MODULE_4__["exportOriginalStyles"])(sketchContext, _objectSpread({
    includeMetadata: true,
    format: 'pretty'
  }, options));
};

/**
 * 获取样式统计信息
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 统计信息
 */
var getStylesStats = function getStylesStats(sketchContext) {
  return Object(_exportStyles__WEBPACK_IMPORTED_MODULE_4__["getStylesStatistics"])(sketchContext);
};

/**
 * 导出样式到剪贴板
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 导出结果
 */
var exportStylesToClipboardFunc = function exportStylesToClipboardFunc(sketchContext) {
  return Object(_exportStyles__WEBPACK_IMPORTED_MODULE_4__["exportStylesToClipboard"])(sketchContext);
};

// 保留原有的管理器类（向后兼容）
var OriginalStylesManager = /*#__PURE__*/function () {
  function OriginalStylesManager(context) {
    _babel_runtime_helpers_classCallCheck__WEBPACK_IMPORTED_MODULE_0___default()(this, OriginalStylesManager);
    this.context = context;
  }
  return _babel_runtime_helpers_createClass__WEBPACK_IMPORTED_MODULE_1___default()(OriginalStylesManager, [{
    key: "getStyles",
    value: function getStyles() {
      return Object(_getOriginalStyles__WEBPACK_IMPORTED_MODULE_3__["getSelectedLayerOriginalStyles"])(this.context);
    }
  }, {
    key: "exportToFile",
    value: function exportToFile() {
      var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      return Object(_exportStyles__WEBPACK_IMPORTED_MODULE_4__["exportOriginalStyles"])(this.context, options);
    }
  }, {
    key: "exportToClipboard",
    value: function exportToClipboard() {
      return exportStylesToClipboardFunc(this.context);
    }
  }, {
    key: "getStatistics",
    value: function getStatistics() {
      return Object(_exportStyles__WEBPACK_IMPORTED_MODULE_4__["getStylesStatistics"])(this.context);
    }
  }, {
    key: "validateSelection",
    value: function validateSelection() {
      return validateLayerSelection(this.context);
    }
  }]);
}();
var createOriginalStylesManager = function createOriginalStylesManager(context) {
  return new OriginalStylesManager(context);
};

/**
 * 完全自包含的原始样式处理函数
 * 在Sketch插件中直接调用，处理所有逻辑包括文件导出
 * @param {Object} sketch - Sketch API对象
 * @param {Object} fs - 文件系统模块
 * @param {Object} path - 路径模块
 * @returns {Object} 处理结果
 */
var processOriginalStyles = function processOriginalStyles(sketch, fs, path) {
  // 1. 获取当前文档和选择
  var document = sketch.getSelectedDocument();
  var selection = document.selectedLayers;
  if (!selection || selection.length === 0) {
    throw new Error('请先选择一个编组或框架');
  }

  // 使用 map 获取所有选中图层的 ID
  var selectedLayerIds = [];
  selection.forEach(function (layer) {
    selectedLayerIds.push(layer.id);
  });

  // 2. 创建上下文对象
  var sketchContext = {
    selection: selection
  };

  // 3. 一键获取并导出原始样式
  var result = getAndExportOriginalStyles(sketchContext);

  // 调试：打印图层结构
  /*   console.log('=== 图层结构 ===');
    console.log(JSON.stringify(result.stylesData, null, 2));
    console.log('=== 结构结束 ==='); */

  // 4. 导出到插件根目录
  var filePath = path.join(process.cwd(), result.exportResult.fileName);
  fs.writeFileSync(filePath, result.exportResult.fileContent, 'utf8');

  // 5. 显示成功消息
  sketch.UI.message("\u539F\u59CB\u6837\u5F0F\u5DF2\u5BFC\u51FA\u5230: ".concat(result.exportResult.fileName));

  // 6. 输出统计信息
  /*   console.log('导出统计:', {
      图层数量: result.statistics.layerCount,
      文件大小: result.statistics.dataSize + ' bytes',
      容器名称: result.statistics.containerName,
      容器类型: result.statistics.containerType
    }); */

  return {
    success: true,
    fileName: result.exportResult.fileName,
    statistics: result.statistics
  };
};


/***/ }),

/***/ "./src/sketchToCss/bordersToCss.js":
/*!*****************************************!*\
  !*** ./src/sketchToCss/bordersToCss.js ***!
  \*****************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/**
 * 将 Sketch 图层的边框样式转换为 Tailwind CSS 类名
 * @param {Object} layer - Sketch 图层对象
 * @returns {string} - Tailwind CSS 类名字符串
 */
/**
 * 将 Sketch 图层的边框样式转换为 Tailwind CSS 类名
 * @param {Object} layer - Sketch 图层对象
 * @returns {string} - Tailwind CSS 类名字符串
 */
var bordersToCss = function bordersToCss(layer) {
  var _layer$style, _layer$style$borderOp;
  // 检查是否有样式和边框
  if (!((_layer$style = layer.style) !== null && _layer$style !== void 0 && _layer$style.borders) || layer.style.borders.length === 0) {
    return '';
  }
  var classes = [];

  // 获取第一个边框样式
  var border = layer.style.borders[0];

  // 检查边框是否启用
  if (!border.enabled) {
    return '';
  }

  // 处理边框宽度
  var borderWidth = Math.round(border.thickness);
  if (borderWidth > 0) {
    // 处理边框位置
    if (border.position === 'Inside') {
      classes.push('border-inset');
    }
    classes.push("border-[".concat(borderWidth, "px]"));
  }

  // 处理边框颜色
  if (border.color) {
    var color = border.color.toLowerCase();

    // 检查颜色是否包含透明度（8位十六进制）
    if (color.length === 9) {
      // 例如 #3a5bcde0
      // 提取颜色部分（不包含透明度）
      var colorHex = color.slice(0, 7);
      // 提取透明度
      var alpha = parseInt(color.slice(7), 16) / 255;

      // 添加边框颜色
      classes.push("border-[".concat(colorHex, "]"));

      // 只有当透明度不是 100% 时才添加透明度类
      if (alpha < 1) {
        classes.push("border-opacity-[".concat(Math.round(alpha * 100), "]"));
      }
    } else {
      // 6位十六进制颜色（无透明度）
      classes.push("border-[".concat(color, "]"));
    }
  }

  // 处理边框样式
  if (border.fillType === 'Color') {
    classes.push('border-solid');
  }

  // 处理圆角
  // 从 borderOptions 中获取圆角信息
  if (((_layer$style$borderOp = layer.style.borderOptions) === null || _layer$style$borderOp === void 0 ? void 0 : _layer$style$borderOp.lineJoin) === 'Round') {
    classes.push('rounded');
  }
  return classes.join(' ');
};
/* harmony default export */ __webpack_exports__["default"] = (bordersToCss);

/***/ }),

/***/ "./src/sketchToCss/test.js":
/*!*********************************!*\
  !*** ./src/sketchToCss/test.js ***!
  \*********************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/defineProperty */ "./node_modules/@babel/runtime/helpers/defineProperty.js");
/* harmony import */ var _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var sketch__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! sketch */ "sketch");
/* harmony import */ var sketch__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(sketch__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _bordersToCss__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./bordersToCss */ "./src/sketchToCss/bordersToCss.js");
/* harmony import */ var _utils_exportToJson__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../utils/exportToJson */ "./src/utils/exportToJson.js");

function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach(function (r) { _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0___default()(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }



var _iterate = function iterate(item, callback) {
  var children = [];
  if (item.layers.length > 0) {
    children = item.layers.map(function (layer) {
      return _iterate(layer, callback);
    });
  }
  return {
    name: item.name,
    style: _objectSpread({}, callback(item)),
    children: children
  };
};
var test = function test() {
  var document = sketch__WEBPACK_IMPORTED_MODULE_1___default.a.getSelectedDocument();
  var page = document.pages[0];
  Object(_utils_exportToJson__WEBPACK_IMPORTED_MODULE_3__["default"])(page, 'page1.json');
  var style = _iterate(page, function (layer) {
    return {
      border: Object(_bordersToCss__WEBPACK_IMPORTED_MODULE_2__["default"])(layer)
    };
  });
  Object(_utils_exportToJson__WEBPACK_IMPORTED_MODULE_3__["default"])(style, 'style.json');
};
/* harmony default export */ __webpack_exports__["default"] = (test);

/***/ }),

/***/ "./src/styleTree/generateStyleTree.js":
/*!********************************************!*\
  !*** ./src/styleTree/generateStyleTree.js ***!
  \********************************************/
/*! exports provided: generateStyleTree */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "generateStyleTree", function() { return _generateStyleTree; });
/* harmony import */ var _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/toConsumableArray */ "./node_modules/@babel/runtime/helpers/toConsumableArray.js");
/* harmony import */ var _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _getCurrentStyle__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./getCurrentStyle */ "./src/styleTree/getCurrentStyle.js");
/* harmony import */ var _getFlexLayoutStyle__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./getFlexLayoutStyle */ "./src/styleTree/getFlexLayoutStyle.js");
/* harmony import */ var _getGridLayoutStyle__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./getGridLayoutStyle */ "./src/styleTree/getGridLayoutStyle.js");




var _generateStyleTree = function generateStyleTree(currentLayer) {
  var parentLayoutType = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'block';
  var parentSize = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
  // 当前节点尺寸
  var currentSize = currentLayer.frame ? {
    width: currentLayer.frame.width,
    height: currentLayer.frame.height
  } : parentSize;

  // 叶子节点（无子 layers）
  if (!currentLayer.layers) {
    // mode 控制宽高类型，flexMode 下传递 parentSize
    var _style = Object(_getCurrentStyle__WEBPACK_IMPORTED_MODULE_1__["default"])(currentLayer, {
      flexMode: parentLayoutType === 'flex',
      parentSize: parentLayoutType === 'flex' ? parentSize : null
    });
    return {
      style: _style,
      children: []
    };
  }

  // 容器节点
  var layers = currentLayer.layers;
  var xList = layers.map(function (layer) {
    return layer.frame.x;
  });
  var yList = layers.map(function (layer) {
    return layer.frame.y;
  });
  console.log('==');
  console.log(currentLayer);
  console.log('==');
  var uniqueXList = _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_0___default()(new Set(xList)).sort(function (a, b) {
    return a - b;
  });
  var uniqueYList = _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_0___default()(new Set(yList)).sort(function (a, b) {
    return a - b;
  });
  var columnCount = uniqueXList.length;
  var rowCount = uniqueYList.length;
  var style, layoutType;
  if (columnCount > 1 && rowCount > 1) {
    style = Object(_getGridLayoutStyle__WEBPACK_IMPORTED_MODULE_3__["getGridLayoutStyle"])(layers, uniqueXList, uniqueYList);
    layoutType = 'grid';
  } else {
    style = Object(_getFlexLayoutStyle__WEBPACK_IMPORTED_MODULE_2__["getFlexLayoutStyle"])(currentLayer, Object(_getCurrentStyle__WEBPACK_IMPORTED_MODULE_1__["default"])(currentLayer, {
      flexMode: parentLayoutType === 'flex',
      parentSize: parentSize
    }), columnCount, rowCount);
    layoutType = 'flex';
  }

  // 递归处理子节点，先按 x 升序，再按 y 升序
  var sortedLayers = _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_0___default()(layers).sort(function (a, b) {
    if (a.frame.x !== b.frame.x) {
      return a.frame.x - b.frame.x;
    }
    return a.frame.y - b.frame.y;
  });
  var children = sortedLayers.map(function (child) {
    return _generateStyleTree(child, layoutType, currentSize);
  });
  return {
    style: style,
    children: children
  };
};


/***/ }),

/***/ "./src/styleTree/getCurrentStyle.js":
/*!******************************************!*\
  !*** ./src/styleTree/getCurrentStyle.js ***!
  \******************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
function getCurrentStyle(layer) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  if (!layer) return {};
  var style = layer.style || {};
  var css = {
    name: layer.name
  };
  var flexMode = options.flexMode === true;
  var parentSize = options.parentSize;

  // 1. frame 相关
  if (typeof layer.name === 'string' && layer.name.startsWith('/')) {
    // 页面级组件，宽高 100%，不管 flexMode
    css.width = '100%';
    css.height = '100%';
  } else if (layer.frame) {
    if (flexMode && parentSize && parentSize.width && parentSize.height) {
      css.maxWidth = (layer.frame.width / parentSize.width * 100).toFixed(2) + '%';
      css.maxHeight = (layer.frame.height / parentSize.height * 100).toFixed(2) + '%';
      css.flex = '1 1 auto';
      css.alignSelf = 'stretch';
    } else if (flexMode) {
      css.maxWidth = layer.frame.width + 'px';
      css.maxHeight = layer.frame.height + 'px';
      css.flex = '1 1 auto';
      css.alignSelf = 'stretch';
    } else {
      css.width = layer.frame.width + 'px';
      css.height = layer.frame.height + 'px';
    }
  }

  // 2. 通用样式
  if (typeof layer.opacity === 'number') {
    css.opacity = layer.opacity;
  }
  if (typeof layer.rotation === 'number' && layer.rotation !== 0) {
    css.transform = "rotate(".concat(layer.rotation, "deg)");
  }

  // 3. 填充（只取第一个 enabled 的 fill）
  if (style.fills && style.fills.length > 0) {
    var fill = style.fills.find(function (f) {
      return f.enabled && f.fillType === 'Color';
    });
    if (fill) {
      css.backgroundColor = fill.color;
    }
  }

  // 4. 边框（只取第一个 enabled 的 border）
  if (style.borders && style.borders.length > 0) {
    var border = style.borders.find(function (b) {
      return b.enabled;
    });
    if (border) {
      css.borderWidth = border.thickness + 'px';
      css.borderColor = border.color;
      css.borderStyle = 'solid';
    }
  }

  // 5. 圆角
  if (typeof style.borderRadius === 'number' && style.borderRadius > 0) {
    css.borderRadius = style.borderRadius + 'px';
  }

  // 6. 阴影（只取第一个 enabled 的 shadow）
  if (style.shadows && style.shadows.length > 0) {
    var shadow = style.shadows.find(function (s) {
      return s.enabled;
    });
    if (shadow) {
      css.boxShadow = "".concat(shadow.offsetX, "px ").concat(shadow.offsetY, "px ").concat(shadow.blurRadius, "px ").concat(shadow.spread || 0, "px ").concat(shadow.color);
    }
  }

  // 7. 文本样式
  if (layer.type === 'Text' && layer.style) {
    if (layer.style.fontSize) css.fontSize = layer.style.fontSize + 'px';
    if (layer.style.fontFamily) css.fontFamily = layer.style.fontFamily;
    if (layer.style.textColor) css.color = layer.style.textColor;
    if (layer.style.fontWeight) css.fontWeight = layer.style.fontWeight;
    if (layer.style.lineHeight) css.lineHeight = layer.style.lineHeight + 'px';
    if (layer.style.letterSpacing) css.letterSpacing = layer.style.letterSpacing + 'px';
    if (layer.style.textAlign) css.textAlign = layer.style.textAlign;
  }

  // 8. 类型标记
  if (layer.type === 'Image' || layer.type === 'Bitmap') {
    css.type = 'img';
  } else {
    css.type = 'ele';
  }
  return css;
}
/* harmony default export */ __webpack_exports__["default"] = (getCurrentStyle);

/***/ }),

/***/ "./src/styleTree/getFlexLayoutStyle.js":
/*!*********************************************!*\
  !*** ./src/styleTree/getFlexLayoutStyle.js ***!
  \*********************************************/
/*! exports provided: getFlexLayoutStyle */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getFlexLayoutStyle", function() { return getFlexLayoutStyle; });
/* harmony import */ var _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/defineProperty */ "./node_modules/@babel/runtime/helpers/defineProperty.js");
/* harmony import */ var _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/helpers/toConsumableArray */ "./node_modules/@babel/runtime/helpers/toConsumableArray.js");
/* harmony import */ var _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1__);


function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach(function (r) { _babel_runtime_helpers_defineProperty__WEBPACK_IMPORTED_MODULE_0___default()(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function getFlexLayoutStyle(currentLayer) {
  var layout = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var columnCount = arguments.length > 2 ? arguments[2] : undefined;
  var rowCount = arguments.length > 3 ? arguments[3] : undefined;
  var children = currentLayer.layers;
  var parentFrame = currentLayer.frame;

  // 生成的布局对象
  var genLayout = {
    display: 'flex'
  };

  // 计算 padding
  var leftPadding = Math.min.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(children.map(function (l) {
    return l.frame.x;
  })));
  var topPadding = Math.min.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(children.map(function (l) {
    return l.frame.y;
  })));
  var rightPadding = currentLayer.frame.width - Math.max.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(children.map(function (l) {
    return l.frame.x + l.frame.width;
  })));
  var bottomPadding = currentLayer.frame.height - Math.max.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(children.map(function (l) {
    return l.frame.y + l.frame.height;
  })));
  genLayout.padding = "".concat(topPadding, "px ").concat(rightPadding, "px ").concat(bottomPadding, "px ").concat(leftPadding, "px");

  // 只有一行，是水平 Flex
  if (rowCount === 1) {
    genLayout.flexDirection = 'row';
    console.log(children);
    var sortedLayers = _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(children).sort(function (a, b) {
      return a.frame.x - b.frame.x;
    });
    var gap = 0;
    if (sortedLayers.length > 1) {
      gap = sortedLayers[1].frame.x - (sortedLayers[0].frame.x + sortedLayers[0].frame.width);
      // 百分比方式
      gap = parentFrame.width > 0 ? gap / parentFrame.width * 100 : 0;
      genLayout.gap = "".concat(gap.toFixed(2), "%");
    } else {
      genLayout.gap = '0%';
    }

    // 推断 justify-content
    var first = sortedLayers[0];
    var last = sortedLayers[sortedLayers.length - 1];
    var spaceLeft = first.frame.x - parentFrame.x;
    var spaceRight = parentFrame.x + parentFrame.width - (last.frame.x + last.frame.width);
    if (spaceLeft === 0 && spaceRight === 0) {
      genLayout.justifyContent = 'space-between';
    } else if (spaceLeft === 0) {
      genLayout.justifyContent = 'flex-start';
    } else if (spaceRight === 0) {
      genLayout.justifyContent = 'flex-end';
    } else {
      // 有 padding 时，居中处理
      genLayout.justifyContent = 'center';
    }

    // 推断 align-items
    var yList = sortedLayers.map(function (l) {
      return l.frame.y;
    });
    var minY = Math.min.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(yList));
    var maxY = Math.max.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(yList));
    if (minY === maxY && minY === parentFrame.y + topPadding) {
      genLayout.alignItems = 'flex-start';
    } else if (minY === maxY && minY === parentFrame.y + parentFrame.height - sortedLayers[0].frame.height - bottomPadding) {
      genLayout.alignItems = 'flex-end';
    } else {
      // 居中或拉伸
      genLayout.alignItems = 'center';
    }
  }
  // 只有一列，是垂直 Flex
  else {
    genLayout.flexDirection = 'column';
    var _sortedLayers = _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(children).sort(function (a, b) {
      return a.frame.y - b.frame.y;
    });
    var _gap = 0;
    if (_sortedLayers.length > 1) {
      _gap = _sortedLayers[1].frame.y - (_sortedLayers[0].frame.y + _sortedLayers[0].frame.height);
      // 百分比方式
      _gap = parentFrame.height > 0 ? _gap / parentFrame.height * 100 : 0;
      genLayout.gap = "".concat(_gap.toFixed(2), "%");
    } else {
      genLayout.gap = '0%';
    }

    // 推断 justify-content
    var _first = _sortedLayers[0];
    var _last = _sortedLayers[_sortedLayers.length - 1];
    var totalChildrenHeight = _sortedLayers.reduce(function (sum, l) {
      return sum + l.frame.height;
    }, 0) + (_sortedLayers.length - 1) * (parentFrame.height * _gap / 100);
    var spaceTop = _first.frame.y - parentFrame.y;
    var spaceBottom = parentFrame.y + parentFrame.height - (_last.frame.y + _last.frame.height);
    if (spaceTop === 0 && spaceBottom === 0) {
      genLayout.justifyContent = 'space-between';
    } else if (spaceTop === 0) {
      genLayout.justifyContent = 'flex-start';
    } else if (spaceBottom === 0) {
      genLayout.justifyContent = 'flex-end';
    } else {
      // 有 padding 时，居中处理
      genLayout.justifyContent = 'center';
    }

    // 推断 align-items
    var xList = _sortedLayers.map(function (l) {
      return l.frame.x;
    });
    var minX = Math.min.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(xList));
    var maxX = Math.max.apply(Math, _babel_runtime_helpers_toConsumableArray__WEBPACK_IMPORTED_MODULE_1___default()(xList));
    if (minX === maxX && minX === parentFrame.x + leftPadding) {
      genLayout.alignItems = 'flex-start';
    } else if (minX === maxX && minX === parentFrame.x + parentFrame.width - _sortedLayers[0].frame.width - rightPadding) {
      genLayout.alignItems = 'flex-end';
    } else {
      genLayout.alignItems = 'center';
    }
  }

  // children 字段，长度为 columnCount * rowCount，每个元素为 { flex: '1 1 auto' }
  var expectedChildrenCount = columnCount * rowCount;
  var childrenLayouts = [];
  for (var i = 0; i < expectedChildrenCount; i++) {
    childrenLayouts.push({
      flex: '1 1 auto'
    });
  }
  genLayout.children = childrenLayouts;

  // 合并传入 layout，传入 layout 优先级高
  return _objectSpread(_objectSpread({}, genLayout), layout);
}


/***/ }),

/***/ "./src/styleTree/getGridLayoutStyle.js":
/*!*********************************************!*\
  !*** ./src/styleTree/getGridLayoutStyle.js ***!
  \*********************************************/
/*! exports provided: getGridLayoutStyle */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getGridLayoutStyle", function() { return getGridLayoutStyle; });
function getGridLayoutStyle(layers, uniqueXList, uniqueYList) {
  var layout = {
    display: 'grid'
  };

  // 从第一行的图层计算 grid-template-columns
  var firstRowLayers = layers.filter(function (layer) {
    return layer.frame.y === uniqueYList[0];
  }).sort(function (a, b) {
    return a.frame.x - b.frame.x;
  });
  layout.gridTemplateColumns = firstRowLayers.map(function (layer) {
    return "".concat(layer.frame.width, "px");
  }).join(' ');

  // 从第一列的图层计算 grid-template-rows
  var firstColLayers = layers.filter(function (layer) {
    return layer.frame.x === uniqueXList[0];
  }).sort(function (a, b) {
    return a.frame.y - b.frame.y;
  });
  layout.gridTemplateRows = firstColLayers.map(function (layer) {
    return "".concat(layer.frame.height, "px");
  }).join(' ');

  // 计算行列间距
  var columnGap = firstRowLayers.length > 1 ? firstRowLayers[1].frame.x - (firstRowLayers[0].frame.x + firstRowLayers[0].frame.width) : 0;
  var rowGap = firstColLayers.length > 1 ? firstColLayers[1].frame.y - (firstColLayers[0].frame.y + firstColLayers[0].frame.height) : 0;
  if (rowGap === columnGap) {
    layout.gap = "".concat(rowGap, "px");
  } else {
    layout.gap = "".concat(rowGap, "px ").concat(columnGap, "px");
  }
  return layout;
}


/***/ }),

/***/ "./src/utils/exportToJson.js":
/*!***********************************!*\
  !*** ./src/utils/exportToJson.js ***!
  \***********************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _skpm_fs__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @skpm/fs */ "./node_modules/@skpm/fs/index.js");
/* harmony import */ var _skpm_fs__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_skpm_fs__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _skpm_path__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @skpm/path */ "./node_modules/@skpm/path/index.js");
/* harmony import */ var _skpm_path__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_skpm_path__WEBPACK_IMPORTED_MODULE_1__);


var exportToJson = function exportToJson(data, fileName) {
  try {
    var filePath = _skpm_path__WEBPACK_IMPORTED_MODULE_1___default.a.join(process.cwd(), fileName);
    if (typeof data === 'string') return _skpm_fs__WEBPACK_IMPORTED_MODULE_0___default.a.writeFileSync(filePath, data, 'utf8');
    return _skpm_fs__WEBPACK_IMPORTED_MODULE_0___default.a.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
  } catch (error) {
    console.error(error);
  }
};
/* harmony default export */ __webpack_exports__["default"] = (exportToJson);

/***/ }),

/***/ "buffer":
/*!*************************!*\
  !*** external "buffer" ***!
  \*************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = require("buffer");

/***/ }),

/***/ "sketch":
/*!*************************!*\
  !*** external "sketch" ***!
  \*************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = require("sketch");

/***/ }),

/***/ "util":
/*!***********************!*\
  !*** external "util" ***!
  \***********************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = require("util");

/***/ })

/******/ });
    if (key === 'default' && typeof exports === 'function') {
      exports(context);
    } else if (typeof exports[key] !== 'function') {
      throw new Error('Missing export named "' + key + '". Your command should contain something like `export function " + key +"() {}`.');
    } else {
      exports[key](context);
    }
  } catch (err) {
    if (typeof process !== 'undefined' && process.listenerCount && process.listenerCount('uncaughtException')) {
      process.emit("uncaughtException", err, "uncaughtException");
    } else {
      throw err
    }
  }
}
globalThis['onRun'] = __skpm_run.bind(this, 'default')

//# sourceMappingURL=__my-command.js.map