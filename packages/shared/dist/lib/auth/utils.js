"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.newPasswordSchema = exports.resetPasswordSchema = exports.registerSchema = exports.loginSchema = void 0;
exports.encrypt = encrypt;
exports.decrypt = decrypt;
exports.createSession = createSession;
exports.deleteSession = deleteSession;
exports.getSession = getSession;
exports.hashPassword = hashPassword;
exports.verifyPassword = verifyPassword;
exports.isValidEmail = isValidEmail;
exports.isStrongPassword = isStrongPassword;
exports.createSessionToken = createSessionToken;
exports.setSessionCookie = setSessionCookie;
exports.getSessionFromCookie = getSessionFromCookie;
exports.clearSessionCookie = clearSessionCookie;
require("server-only");
var jose_1 = require("jose");
var headers_1 = require("next/headers");
var zod_1 = require("zod");
var bcryptjs_1 = require("bcryptjs");
var secretKey = process.env.JWT_SECRET;
var key = new TextEncoder().encode(secretKey);
function encrypt(payload) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, new jose_1.SignJWT(payload)
                        .setProtectedHeader({ alg: 'HS256' })
                        .setIssuedAt()
                        .setExpirationTime('1d')
                        .sign(key)];
                case 1: return [2 /*return*/, _a.sent()];
            }
        });
    });
}
function decrypt(input) {
    return __awaiter(this, void 0, void 0, function () {
        var payload;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, jose_1.jwtVerify)(input, key, {
                        algorithms: ['HS256'],
                    })];
                case 1:
                    payload = (_a.sent()).payload;
                    return [2 /*return*/, payload];
            }
        });
    });
}
function createSession(userId) {
    return __awaiter(this, void 0, void 0, function () {
        var expires, session;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    expires = new Date(Date.now() + 24 * 60 * 60 * 1000);
                    return [4 /*yield*/, encrypt({ userId: userId, expires: expires })];
                case 1:
                    session = _a.sent();
                    (0, headers_1.cookies)().set('session', session, {
                        httpOnly: true,
                        secure: process.env.NODE_ENV === 'production',
                        expires: expires,
                        sameSite: 'lax',
                        path: '/',
                    });
                    return [2 /*return*/];
            }
        });
    });
}
function deleteSession() {
    (0, headers_1.cookies)().delete('session');
}
function getSession() {
    return __awaiter(this, void 0, void 0, function () {
        var session;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    session = (_a = (0, headers_1.cookies)().get('session')) === null || _a === void 0 ? void 0 : _a.value;
                    if (!session)
                        return [2 /*return*/, null];
                    return [4 /*yield*/, decrypt(session)];
                case 1: return [2 /*return*/, _b.sent()];
            }
        });
    });
}
// Validation schemas
exports.loginSchema = zod_1.z.object({
    email: zod_1.z.string().email('Invalid email address'),
    password: zod_1.z.string().min(6, 'Password must be at least 6 characters'),
});
exports.registerSchema = zod_1.z.object({
    name: zod_1.z.string().min(2, 'Name must be at least 2 characters'),
    email: zod_1.z.string().email('Invalid email address'),
    password: zod_1.z.string().min(6, 'Password must be at least 6 characters'),
});
exports.resetPasswordSchema = zod_1.z.object({
    email: zod_1.z.string().email('Invalid email address'),
});
exports.newPasswordSchema = zod_1.z.object({
    password: zod_1.z.string().min(6, 'Password must be at least 6 characters'),
    confirmPassword: zod_1.z.string(),
}).refine(function (data) { return data.password === data.confirmPassword; }, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
});
// Additional helpers expected by API routes
function hashPassword(password) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, bcryptjs_1.hash)(password, 12)];
                case 1: return [2 /*return*/, _a.sent()];
            }
        });
    });
}
function verifyPassword(password, hashed) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, bcryptjs_1.compare)(password, hashed)];
                case 1: return [2 /*return*/, _a.sent()];
            }
        });
    });
}
function isValidEmail(email) {
    return zod_1.z.string().email().safeParse(email).success;
}
function isStrongPassword(password) {
    var minLength = 8;
    var hasLower = /[a-z]/.test(password);
    var hasUpper = /[A-Z]/.test(password);
    var hasNumber = /\d/.test(password);
    var hasSpecial = /[^A-Za-z0-9]/.test(password);
    if (password.length < minLength)
        return { valid: false, message: "Password must be at least ".concat(minLength, " characters") };
    if (!hasLower || !hasUpper)
        return { valid: false, message: 'Password must include both upper and lower case letters' };
    if (!hasNumber)
        return { valid: false, message: 'Password must include at least one number' };
    if (!hasSpecial)
        return { valid: false, message: 'Password must include at least one special character' };
    return { valid: true };
}
function createSessionToken(payload) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, new jose_1.SignJWT(payload)
                        .setProtectedHeader({ alg: 'HS256' })
                        .setIssuedAt()
                        .setExpirationTime('7d')
                        .sign(key)];
                case 1: return [2 /*return*/, _a.sent()];
            }
        });
    });
}
function setSessionCookie(token) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            (0, headers_1.cookies)().set('omni_session', token, {
                httpOnly: true,
                secure: process.env.NODE_ENV === 'production',
                sameSite: 'lax',
                path: '/',
                maxAge: 60 * 60 * 24 * 7,
            });
            return [2 /*return*/];
        });
    });
}
function getSessionFromCookie() {
    return __awaiter(this, void 0, void 0, function () {
        var token, payload, _a;
        var _b;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    token = (_b = (0, headers_1.cookies)().get('omni_session')) === null || _b === void 0 ? void 0 : _b.value;
                    if (!token)
                        return [2 /*return*/, null];
                    _c.label = 1;
                case 1:
                    _c.trys.push([1, 3, , 4]);
                    return [4 /*yield*/, (0, jose_1.jwtVerify)(token, key, { algorithms: ['HS256'] })];
                case 2:
                    payload = (_c.sent()).payload;
                    return [2 /*return*/, payload];
                case 3:
                    _a = _c.sent();
                    return [2 /*return*/, null];
                case 4: return [2 /*return*/];
            }
        });
    });
}
function clearSessionCookie() {
    (0, headers_1.cookies)().delete('omni_session');
}
//# sourceMappingURL=utils.js.map