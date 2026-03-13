import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged,
  getRedirectResult
} from 'firebase/auth';
import { auth } from '@/firebase';
import { setAuthToken } from '@/services/api';
import { authService } from '@/services/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Listen to Firebase auth state changes
  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      try {
        // 1. First process any pending redirect results
        const result = await getRedirectResult(auth);
        if (result?.user) {
          console.log("Redirect result found", result.user.email);
          const idToken = await result.user.getIdToken();
          setToken(idToken);
          setAuthToken(idToken);
          // Ensure the user exists in our SQL backend
          await authService.googleLogin(result.user.displayName || 'User', result.user.email);
        }
      } catch (err) {
        console.error('Redirect sign-in error:', err);
      }

      // 2. Then set up the auth state listener
      const unsubscribe = onAuthStateChanged(auth, async (fbUser) => {
        if (!isMounted) return;
        setFirebaseUser(fbUser);
        
        if (fbUser) {
          try {
            const idToken = await fbUser.getIdToken();
            setToken(idToken);
            setAuthToken(idToken);
            
            await checkUser();
          } catch (error) {
             if (error.response && error.response.status === 404) {
               // User is in Firebase but not in our SQL backend yet.
               console.log("User not in DB, sycing from Firebase...");
               try {
                 await authService.googleLogin(fbUser.displayName || 'User', fbUser.email);
                 await checkUser();
               } catch (syncError) {
                 console.error("Failed to sync user:", syncError);
                 setUser(null);
               }
             } else {
               console.error('Failed to fetch user profile:', error);
               setUser(null);
             }
          }
        } else {
          setToken(null);
          setAuthToken(null);
          setUser(null);
        }
        
        // Only set loading false after everything is processed
        setLoading(false);
      });

      return unsubscribe;
    };

    const unsubscribePromise = initAuth();

    return () => {
      isMounted = false;
      unsubscribePromise.then(unsub => unsub && unsub());
    };
  }, []);

  const checkUser = async () => {
    try {
      const userProfile = await authService.getProfile();
      setUser(userProfile);
      return userProfile;
    } catch (error) {
      if (error.response && error.response.status === 404) {
        // User authenticated in Firebase but not in DB -> clear user profile
        setUser(null);
      } else {
        throw error;
      }
    }
  };

  // Refresh token periodically (Firebase tokens expire after 1 hour)
  useEffect(() => {
    if (!firebaseUser) return;

    const refreshToken = async () => {
      try {
        const newToken = await firebaseUser.getIdToken(true);
        setToken(newToken);
        setAuthToken(newToken);
      } catch (error) {
        console.error('Failed to refresh token:', error);
      }
    };

    // Refresh token every 55 minutes
    const interval = setInterval(refreshToken, 55 * 60 * 1000);
    return () => clearInterval(interval);
  }, [firebaseUser]);

  const login = async (email, password) => {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const idToken = await userCredential.user.getIdToken();
    setToken(idToken);
    setAuthToken(idToken);
    
    // Fetch user profile
    const userProfile = await authService.getProfile();
    setUser(userProfile);
    
    return userProfile;
  };

  const register = async (email, password, name, initial_level) => {
    // Create Firebase user
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const idToken = await userCredential.user.getIdToken();
    setToken(idToken);
    setAuthToken(idToken);
    
    // Create user profile in backend
    const userProfile = await authService.register(name, initial_level);
    
    setUser(userProfile);
    return userProfile;
  };

  const logout = async () => {
    await signOut(auth);
    setToken(null);
    setAuthToken(null);
    setUser(null);
  };

  const getAxiosConfig = () => ({
    headers: { Authorization: `Bearer ${token}` }
  });

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        checkUser,
        getAxiosConfig,
        isAuthenticated: !!token && !!user
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
