"use strict";
'use client';
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
exports.useAuth = exports.AuthProvider = void 0;
var react_1 = require("react");
var navigation_1 = require("next/navigation");
var auth_1 = require("../lib/auth");
var AuthContext = (0, react_1.createContext)(undefined);
var AuthProvider = function (_a) {
    var children = _a.children;
    var _b = (0, react_1.useState)(null), user = _b[0], setUser = _b[1];
    var _c = (0, react_1.useState)(null), token = _c[0], setToken = _c[1];
    var _d = (0, react_1.useState)(true), loading = _d[0], setLoading = _d[1];
    var router = (0, navigation_1.useRouter)();
    (0, react_1.useEffect)(function () {
        // Check for stored token on initial load
        var storedToken = localStorage.getItem('auth_token');
        if (storedToken) {
            setToken(storedToken);
            // TODO: Validate token with backend
        }
        setLoading(false);
    }, []);
    // Sign in with email and password
    var signIn = function (email, password) { return __awaiter(void 0, void 0, void 0, function () {
        var data, error_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, auth_1.authApi.login(email, password)];
                case 1:
                    data = _a.sent();
                    setUser(data.user);
                    setToken(data.access_token);
                    localStorage.setItem('auth_token', data.access_token);
                    router.push('/dashboard');
                    return [2 /*return*/, { data: data, error: null }];
                case 2:
                    error_1 = _a.sent();
                    return [2 /*return*/, { data: null, error: error_1 instanceof Error ? error_1.message : 'Login failed' }];
                case 3: return [2 /*return*/];
            }
        });
    }); };
    // Sign up with email and password
    var signUp = function (email, password, fullName) { return __awaiter(void 0, void 0, void 0, function () {
        var username, data, error_2;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    username = email.split('@')[0];
                    return [4 /*yield*/, auth_1.authApi.signup(email, username, password, fullName)];
                case 1:
                    data = _a.sent();
                    router.push('/auth/login?message=Account created successfully');
                    return [2 /*return*/, { data: data, error: null }];
                case 2:
                    error_2 = _a.sent();
                    return [2 /*return*/, { data: null, error: error_2 instanceof Error ? error_2.message : 'Signup failed' }];
                case 3: return [2 /*return*/];
            }
        });
    }); };
    // Sign out
    var signOut = function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            setUser(null);
            setToken(null);
            localStorage.removeItem('auth_token');
            router.push('/auth/login');
            return [2 /*return*/];
        });
    }); };
    // Sign in with Google (placeholder)
    var signInWithGoogle = function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, { data: null, error: 'Google OAuth not implemented' }];
        });
    }); };
    // Sign in with GitHub (placeholder)
    var signInWithGithub = function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, { data: null, error: 'GitHub OAuth not implemented' }];
        });
    }); };
    var value = {
        user: user,
        token: token,
        loading: loading,
        signIn: signIn,
        signUp: signUp,
        signOut: signOut,
        signInWithGoogle: signInWithGoogle,
        signInWithGithub: signInWithGithub,
    };
    return (<AuthContext.Provider value={value}>
      {!loading ? children : (<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading OmniVid...</p>
          </div>
        </div>)}
    </AuthContext.Provider>);
};
exports.AuthProvider = AuthProvider;
var useAuth = function () {
    var context = (0, react_1.useContext)(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
exports.useAuth = useAuth;
//# sourceMappingURL=AuthContext.jsx.map