import { useEffect } from 'react';
import { useGoogleLogin } from '@react-oauth/google';

const GoogleSignIn = ({ onSuccess, onError }) => {
    const login = useGoogleLogin({
        onSuccess: async (response) => {
            try {
                const result = await fetch('/auth/google', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        id_token: response.credential
                    }),
                });
                
                if (!result.ok) {
                    throw new Error('Authentication failed');
                }
                
                const data = await result.json();
                onSuccess(data.user);
                
            } catch (error) {
                console.error('Sign-in error:', error);
                onError(error);
            }
        },
        onError: (error) => {
            console.error('Google sign-in error:', error);
            onError(error);
        }
    });

    return (
        <button 
            onClick={() => login()}
            className="google-signin-button"
        >
            Sign in with Google
        </button>
    );
};

export default GoogleSignIn;
