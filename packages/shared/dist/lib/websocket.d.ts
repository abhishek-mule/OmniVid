import { ReactNode } from 'react';
type WebSocketContextType = {
    isConnected: boolean;
    progress: number;
    currentStage: string;
    error: string | null;
    sendMessage: (message: any) => boolean;
};
type WebSocketProviderProps = {
    children: ReactNode;
    url: string;
};
export declare function WebSocketProvider({ children, url }: WebSocketProviderProps): import("react").JSX.Element;
export declare function useWebSocket(): WebSocketContextType;
export {};
