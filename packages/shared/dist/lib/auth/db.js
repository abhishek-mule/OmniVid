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
exports.prisma = void 0;
exports.getUserByEmail = getUserByEmail;
exports.findUserByEmail = findUserByEmail;
exports.createUser = createUser;
exports.updateUser = updateUser;
exports.createPasswordResetToken = createPasswordResetToken;
exports.verifyPasswordResetToken = verifyPasswordResetToken;
exports.deletePasswordResetToken = deletePasswordResetToken;
exports.getUserByAccount = getUserByAccount;
exports.linkAccount = linkAccount;
exports.findUserById = findUserById;
exports.updateUserPassword = updateUserPassword;
exports.deleteUserSessions = deleteUserSessions;
exports.createSession = createSession;
exports.findSessionByToken = findSessionByToken;
exports.deleteSession = deleteSession;
exports.findPasswordResetToken = findPasswordResetToken;
exports.markTokenAsUsed = markTokenAsUsed;
exports.findOrCreateOAuthUser = findOrCreateOAuthUser;
var client_1 = require("@prisma/client");
exports.prisma = global.prisma || new client_1.PrismaClient();
if (process.env.NODE_ENV !== 'production') {
    global.prisma = exports.prisma;
}
// Helper function to get user by email
function getUserByEmail(email) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.user.findUnique({
                    where: { email: email },
                })];
        });
    });
}
// Alias to match API imports
function findUserByEmail(email) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.user.findUnique({
                    where: { email: email },
                    include: { accounts: true },
                })];
        });
    });
}
// Helper function to create a new user
function createUser(data) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.user.create({
                    data: data,
                })];
        });
    });
}
// Helper function to update user
function updateUser(id, data) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.user.update({
                    where: { id: id },
                    data: data,
                })];
        });
    });
}
// Helper function to create password reset token
function createPasswordResetToken(userId) {
    return __awaiter(this, void 0, void 0, function () {
        var token, expires, created;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    token = crypto.randomUUID();
                    expires = new Date(Date.now() + 60 * 60 * 1000);
                    return [4 /*yield*/, exports.prisma.passwordResetToken.create({
                            data: { userId: userId, token: token, expires: expires, used: false },
                        })];
                case 1:
                    created = _a.sent();
                    return [2 /*return*/, created];
            }
        });
    });
}
// Helper function to verify password reset token
function verifyPasswordResetToken(token) {
    return __awaiter(this, void 0, void 0, function () {
        var resetToken;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, exports.prisma.passwordResetToken.findUnique({
                        where: { token: token },
                    })];
                case 1:
                    resetToken = _a.sent();
                    if (!resetToken)
                        return [2 /*return*/, null];
                    if (new Date() > resetToken.expires)
                        return [2 /*return*/, null];
                    return [2 /*return*/, resetToken];
            }
        });
    });
}
// Helper function to delete password reset token
function deletePasswordResetToken(token) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, exports.prisma.passwordResetToken.delete({
                        where: { token: token },
                    })];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
// Helper function to get user by account
function getUserByAccount(provider, providerAccountId) {
    return __awaiter(this, void 0, void 0, function () {
        var account;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0: return [4 /*yield*/, exports.prisma.account.findUnique({
                        where: {
                            provider_providerAccountId: {
                                provider: provider,
                                providerAccountId: providerAccountId,
                            },
                        },
                        select: { user: true },
                    })];
                case 1:
                    account = _b.sent();
                    return [2 /*return*/, (_a = account === null || account === void 0 ? void 0 : account.user) !== null && _a !== void 0 ? _a : null];
            }
        });
    });
}
// Helper function to link account to user
function linkAccount(userId, provider, providerAccountId, accessToken, refreshToken) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, exports.prisma.account.upsert({
                        where: {
                            provider_providerAccountId: {
                                provider: provider,
                                providerAccountId: providerAccountId,
                            },
                        },
                        update: {
                            access_token: accessToken,
                            refresh_token: refreshToken,
                        },
                        create: {
                            userId: userId,
                            type: 'oauth',
                            provider: provider,
                            providerAccountId: providerAccountId,
                            access_token: accessToken,
                            refresh_token: refreshToken,
                        },
                    })];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
// Added exports to support API routes
function findUserById(id) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.user.findUnique({
                    where: { id: id },
                    include: { accounts: true },
                })];
        });
    });
}
function updateUserPassword(userId, password) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.user.update({
                    where: { id: userId },
                    data: { password: password },
                })];
        });
    });
}
function deleteUserSessions(userId) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.session.deleteMany({
                    where: { userId: userId },
                })];
        });
    });
}
function createSession(data) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.session.create({
                    data: data,
                })];
        });
    });
}
function findSessionByToken(sessionToken) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.session.findUnique({
                    where: { sessionToken: sessionToken },
                    include: { user: true },
                })];
        });
    });
}
function deleteSession(sessionToken) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.session.delete({
                    where: { sessionToken: sessionToken },
                })];
        });
    });
}
function findPasswordResetToken(token) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.passwordResetToken.findUnique({
                    where: { token: token },
                    include: { user: true },
                })];
        });
    });
}
function markTokenAsUsed(tokenId) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, exports.prisma.passwordResetToken.update({
                    where: { id: tokenId },
                    data: { used: true },
                })];
        });
    });
}
function findOrCreateOAuthUser(data) {
    return __awaiter(this, void 0, void 0, function () {
        var existingAccount, existingUser, newUser;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, exports.prisma.account.findUnique({
                        where: {
                            provider_providerAccountId: {
                                provider: data.provider,
                                providerAccountId: data.providerAccountId,
                            },
                        },
                        include: { user: true },
                    })];
                case 1:
                    existingAccount = _a.sent();
                    if (existingAccount) {
                        return [2 /*return*/, existingAccount.user];
                    }
                    return [4 /*yield*/, getUserByEmail(data.email)];
                case 2:
                    existingUser = _a.sent();
                    if (!existingUser) return [3 /*break*/, 4];
                    return [4 /*yield*/, linkAccount(existingUser.id, data.provider, data.providerAccountId, data.access_token, data.refresh_token)];
                case 3:
                    _a.sent();
                    return [2 /*return*/, existingUser];
                case 4: return [4 /*yield*/, exports.prisma.user.create({
                        data: {
                            email: data.email,
                            name: data.name,
                            image: data.image,
                            emailVerified: true,
                            accounts: {
                                create: {
                                    type: 'oauth',
                                    provider: data.provider,
                                    providerAccountId: data.providerAccountId,
                                    access_token: data.access_token,
                                    refresh_token: data.refresh_token,
                                },
                            },
                        },
                    })];
                case 5:
                    newUser = _a.sent();
                    return [2 /*return*/, newUser];
            }
        });
    });
}
//# sourceMappingURL=db.js.map