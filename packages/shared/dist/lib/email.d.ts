type EmailParams = {
    to: string;
    name: string;
    resetUrl: string;
};
export declare function sendPasswordResetEmail({ to, name, resetUrl }: EmailParams): Promise<void>;
export declare function sendVerificationEmail({ to, name, verifyUrl }: {
    to: string;
    name: string;
    verifyUrl: string;
}): Promise<void>;
export {};
