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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.simpleApi = exports.healthApi = exports.videoApi = void 0;
var axios_1 = __importDefault(require("axios"));
var API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
var API_V1_PREFIX = '/api/v1';
// Create axios instance
var apiClient = axios_1.default.create({
    baseURL: "".concat(API_BASE_URL).concat(API_V1_PREFIX),
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds
});
// Request interceptor
apiClient.interceptors.request.use(function (config) {
    // Add auth token if available
    var token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = "Bearer ".concat(token);
    }
    return config;
}, function (error) {
    return Promise.reject(error);
});
// Response interceptor
apiClient.interceptors.response.use(function (response) { return response; }, function (error) {
    var _a;
    if (((_a = error.response) === null || _a === void 0 ? void 0 : _a.status) === 401) {
        // Handle unauthorized
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
    }
    return Promise.reject(error);
});
// API Methods
exports.videoApi = {
    /**
     * Create a new video generation request
     */
    createVideo: function (data) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, apiClient.post('/videos/', data)];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.data];
                }
            });
        });
    },
    /**
     * Get video status and details
     */
    getVideo: function (videoId) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, apiClient.get("/videos/".concat(videoId))];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.data];
                }
            });
        });
    },
    /**
     * List all videos with pagination
     */
    listVideos: function (params) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, apiClient.get('/videos/', { params: params })];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.data];
                }
            });
        });
    },
    /**
     * Download video file
     */
    getDownloadUrl: function (videoId) {
        return "".concat(API_BASE_URL).concat(API_V1_PREFIX, "/videos/").concat(videoId, "/download");
    },
    /**
     * Delete a video
     */
    deleteVideo: function (videoId) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, apiClient.delete("/videos/".concat(videoId))];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.data];
                }
            });
        });
    },
    /**
     * Cancel video generation
     */
    cancelVideo: function (videoId) {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, apiClient.post("/videos/".concat(videoId, "/cancel"))];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.data];
                }
            });
        });
    },
};
// Health check
exports.healthApi = {
    check: function () {
        return __awaiter(this, void 0, void 0, function () {
            var response;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, axios_1.default.get("".concat(API_BASE_URL, "/health"))];
                    case 1:
                        response = _a.sent();
                        return [2 /*return*/, response.data];
                }
            });
        });
    },
};
function httpToWs(url) {
    if (url.startsWith('https://'))
        return url.replace('https://', 'wss://');
    if (url.startsWith('http://'))
        return url.replace('http://', 'ws://');
    return url;
}
// Simplified API for template and video operations
exports.simpleApi = {
    listTemplates: function () {
        return __awaiter(this, void 0, void 0, function () {
            var res, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _b.trys.push([0, 2, , 3]);
                        return [4 /*yield*/, axios_1.default.get("".concat(API_BASE_URL, "/templates"))];
                    case 1:
                        res = _b.sent();
                        return [2 /*return*/, Array.isArray(res.data) ? res.data : []];
                    case 2:
                        _a = _b.sent();
                        return [2 /*return*/, []];
                    case 3: return [2 /*return*/];
                }
            });
        });
    },
    createVideo: function (payload) {
        return __awaiter(this, void 0, void 0, function () {
            var data, resp;
            var _a, _b, _c, _d, _e;
            return __generator(this, function (_f) {
                switch (_f.label) {
                    case 0:
                        data = {
                            prompt: payload.prompt,
                            resolution: ((_a = payload === null || payload === void 0 ? void 0 : payload.settings) === null || _a === void 0 ? void 0 : _a.resolution) || '1080p',
                            fps: ((_b = payload === null || payload === void 0 ? void 0 : payload.settings) === null || _b === void 0 ? void 0 : _b.fps) || 30,
                            duration: ((_c = payload === null || payload === void 0 ? void 0 : payload.settings) === null || _c === void 0 ? void 0 : _c.duration) || 15,
                            quality: ((_d = payload === null || payload === void 0 ? void 0 : payload.settings) === null || _d === void 0 ? void 0 : _d.quality) || 'balanced',
                            render_engine: ((_e = payload === null || payload === void 0 ? void 0 : payload.settings) === null || _e === void 0 ? void 0 : _e.render_engine) || 'remotion',
                        };
                        return [4 /*yield*/, exports.videoApi.createVideo(data)];
                    case 1:
                        resp = _f.sent();
                        return [2 /*return*/, { video_id: resp.id }];
                }
            });
        });
    },
    getWebSocketUrl: function (videoId) {
        var base = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
        return "".concat(httpToWs(base), "/ws/videos/").concat(videoId);
    },
    getDownloadUrl: function (videoId) {
        return exports.videoApi.getDownloadUrl(videoId);
    },
};
exports.default = apiClient;
//# sourceMappingURL=api.js.map