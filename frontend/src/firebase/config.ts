// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDdQoKIIFRcTXTOA8Xum3WHjYerOceli_w",
  authDomain: "personalize-recommdation.firebaseapp.com",
  projectId: "personalize-recommdation",
  storageBucket: "personalize-recommdation.firebasestorage.app",
  messagingSenderId: "166509162597",
  appId: "1:166509162597:web:597304223032bdee6e568c",
  measurementId: "G-JDQH7DT06F"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Analytics only if supported (prevents errors in development)
isSupported().then(yes => yes ? getAnalytics(app) : null);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Debug: Check if auth is initialized
console.log('Firebase auth initialized:', !!auth);

export default app;