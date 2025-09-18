// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";
import { getFirestore } from "firebase/firestore";
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

// Initialize Firebase Storage
export const storage = getStorage(app);

// Initialize Firestore
export const db = getFirestore(app);

// Debug: Check if services are initialized
console.log('Firebase auth initialized:', !!auth);
console.log('Firebase storage initialized:', !!storage);
console.log('Firebase firestore initialized:', !!db);

export default app;