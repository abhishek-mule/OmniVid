"use strict";
'use server';
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
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
exports.login = login;
exports.register = register;
exports.logout = logout;
exports.requestPasswordReset = requestPasswordReset;
exports.resetPassword = resetPassword;
exports.getCurrentUser = getCurrentUser;
exports.requireAuth = requireAuth;
exports.handleOAuthCallback = handleOAuthCallback;
var navigation_1 = require("next/navigation");
var bcryptjs_1 = require("bcryptjs");
var zod_1 = require("zod");
var utils_1 = require("./utils");
var db = __importStar(require("./db"));
var email_1 = require("../email");
// Login action
function login(formData) {
    return __awaiter(this, void 0, void 0, function () {
        var email, password, success, user, isValid, error_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    email = formData.get('email');
                    password = formData.get('password');
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 5, , 6]);
                    success = zod_1.z.object({
                        email: zod_1.z.string().email(),
                        password: zod_1.z.string().min(6),
                    }).safeParse({ email: email, password: password }).success;
                    if (!success) {
                        return [2 /*return*/, { error: 'Invalid input' }];
                    }
                    return [4 /*yield*/, db.getUserByEmail(email)];
                case 2:
                    user = _a.sent();
                    if (!user || !user.password) {
                        return [2 /*return*/, { error: 'Invalid credentials' }];
                    }
                    return [4 /*yield*/, (0, bcryptjs_1.compare)(password, user.password)];
                case 3:
                    isValid = _a.sent();
                    if (!isValid) {
                        return [2 /*return*/, { error: 'Invalid credentials' }];
                    }
                    // Create session
                    return [4 /*yield*/, (0, utils_1.createSession)(user.id)];
                case 4:
                    // Create session
                    _a.sent();
                    return [2 /*return*/, { success: true }];
                case 5:
                    error_1 = _a.sent();
                    console.error('Login error:', error_1);
                    return [2 /*return*/, { error: 'An error occurred during login' }];
                case 6: return [2 /*return*/];
            }
        });
    });
}
// Register action
function register(formData) {
    return __awaiter(this, void 0, void 0, function () {
        var name, email, password, success, existingUser, hashedPassword, user, error_2;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    name = formData.get('name');
                    email = formData.get('email');
                    password = formData.get('password');
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 6, , 7]);
                    success = zod_1.z.object({
                        name: zod_1.z.string().min(2),
                        email: zod_1.z.string().email(),
                        password: zod_1.z.string().min(6),
                    }).safeParse({ name: name, email: email, password: password }).success;
                    if (!success) {
                        return [2 /*return*/, { error: 'Invalid input' }];
                    }
                    return [4 /*yield*/, db.getUserByEmail(email)];
                case 2:
                    existingUser = _a.sent();
                    if (existingUser) {
                        return [2 /*return*/, { error: 'User already exists' }];
                    }
                    return [4 /*yield*/, (0, bcryptjs_1.hash)(password, 12)];
                case 3:
                    hashedPassword = _a.sent();
                    return [4 /*yield*/, db.createUser({
                            name: name,
                            email: email,
                            password: hashedPassword,
                        })];
                case 4:
                    user = _a.sent();
                    // Create session
                    return [4 /*yield*/, (0, utils_1.createSession)(user.id)];
                case 5:
                    // Create session
                    _a.sent();
                    return [2 /*return*/, { success: true }];
                case 6:
                    error_2 = _a.sent();
                    console.error('Registration error:', error_2);
                    return [2 /*return*/, { error: 'An error occurred during registration' }];
                case 7: return [2 /*return*/];
            }
        });
    });
}
// Logout action
function logout() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            (0, utils_1.deleteSession)();
            (0, navigation_1.redirect)('/auth/login');
            return [2 /*return*/];
        });
    });
}
// Request password reset
function requestPasswordReset(formData) {
    return __awaiter(this, void 0, void 0, function () {
        var email, user, created, token, resetUrl, error_3;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    email = formData.get('email');
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 5, , 6]);
                    return [4 /*yield*/, db.getUserByEmail(email)];
                case 2:
                    user = _a.sent();
                    if (!user) {
                        // Don't reveal if the user exists or not
                        return [2 /*return*/, { success: true }];
                    }
                    return [4 /*yield*/, db.createPasswordResetToken(user.id)];
                case 3:
                    created = _a.sent();
                    token = created.token;
                    resetUrl = "".concat(process.env.NEXT_PUBLIC_APP_URL, "/auth/reset-password?token=").concat(token);
                    return [4 /*yield*/, (0, email_1.sendPasswordResetEmail)({
                            to: email,
                            name: user.name || 'User',
                            resetUrl: resetUrl,
                        })];
                case 4:
                    _a.sent();
                    return [2 /*return*/, { success: true }];
                case 5:
                    error_3 = _a.sent();
                    console.error('Password reset request error:', error_3);
                    return [2 /*return*/, { error: 'An error occurred while processing your request' }];
                case 6: return [2 /*return*/];
            }
        });
    });
}
// Reset password
function resetPassword(formData) {
    return __awaiter(this, void 0, void 0, function () {
        var token, password, confirmPassword, resetToken, user, hashedPassword, error_4;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    token = formData.get('token');
                    password = formData.get('password');
                    confirmPassword = formData.get('confirmPassword');
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 8, , 9]);
                    // Validate input
                    if (password !== confirmPassword) {
                        return [2 /*return*/, { error: 'Passwords do not match' }];
                    }
                    return [4 /*yield*/, db.verifyPasswordResetToken(token)];
                case 2:
                    resetToken = _a.sent();
                    if (!resetToken) {
                        return [2 /*return*/, { error: 'Invalid or expired token' }];
                    }
                    return [4 /*yield*/, db.findUserById(resetToken.userId)];
                case 3:
                    user = _a.sent();
                    if (!user) {
                        return [2 /*return*/, { error: 'User not found' }];
                    }
                    return [4 /*yield*/, (0, bcryptjs_1.hash)(password, 12)];
                case 4:
                    hashedPassword = _a.sent();
                    return [4 /*yield*/, db.updateUserPassword(user.id, hashedPassword)];
                case 5:
                    _a.sent();
                    // Delete used token
                    return [4 /*yield*/, db.deletePasswordResetToken(token)];
                case 6:
                    // Delete used token
                    _a.sent();
                    // Log the user in
                    return [4 /*yield*/, (0, utils_1.createSession)(user.id)];
                case 7:
                    // Log the user in
                    _a.sent();
                    return [2 /*return*/, { success: true }];
                case 8:
                    error_4 = _a.sent();
                    console.error('Password reset error:', error_4);
                    return [2 /*return*/, { error: 'An error occurred while resetting your password' }];
                case 9: return [2 /*return*/];
            }
        });
    });
}
// Get current user
function getCurrentUser() {
    return __awaiter(this, void 0, void 0, function () {
        var session;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, utils_1.getSession)()];
                case 1:
                    session = _a.sent();
                    if (!session)
                        return [2 /*return*/, null];
                    return [4 /*yield*/, db.findUserById(session.userId)];
                case 2: return [2 /*return*/, _a.sent()];
            }
        });
    });
}
// Require authentication
function requireAuth() {
    return __awaiter(this, void 0, void 0, function () {
        var user;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, getCurrentUser()];
                case 1:
                    user = _a.sent();
                    if (!user) {
                        (0, navigation_1.redirect)('/auth/login');
                    }
                    return [2 /*return*/, user];
            }
        });
    });
}
// OAuth callback
function handleOAuthCallback(provider, profile, accessToken, refreshToken) {
    return __awaiter(this, void 0, void 0, function () {
        var user, error_5;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 3, , 4]);
                    return [4 /*yield*/, db.findOrCreateOAuthUser({
                            email: profile.email,
                            name: profile.name || profile.email.split('@')[0],
                            image: profile.image,
                            provider: provider,
                            providerAccountId: profile.id,
                            access_token: accessToken,
                            refresh_token: refreshToken,
                        })];
                case 1:
                    user = _a.sent();
                    // Create session
                    return [4 /*yield*/, (0, utils_1.createSession)(user.id)];
                case 2:
                    // Create session
                    _a.sent();
                    return [2 /*return*/, { success: true }];
                case 3:
                    error_5 = _a.sent();
                    console.error('OAuth callback error:', error_5);
                    return [2 /*return*/, { error: 'An error occurred during authentication' }];
                case 4: return [2 /*return*/];
            }
        });
    });
}
//# sourceMappingURL=server-actions.js.map