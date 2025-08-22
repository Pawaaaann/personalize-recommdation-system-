# Firebase Authentication Setup Guide

This guide will help you set up Firebase Authentication for your EduRec recommendation system.

## Prerequisites

- A Google account
- Node.js and npm installed on your system

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter a project name (e.g., "edurec-auth")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project console, click on "Authentication" in the left sidebar
2. Click "Get started"
3. Go to the "Sign-in method" tab
4. Enable the following providers:
   - **Email/Password**: Click "Enable" and save
   - **Google**: Click "Enable", choose a project support email, and save

## Step 3: Get Firebase Configuration

1. In your Firebase project console, click on the gear icon (⚙️) next to "Project Overview"
2. Select "Project settings"
3. Scroll down to "Your apps" section
4. Click the web icon (</>)
5. Enter an app nickname (e.g., "edurec-web")
6. Click "Register app"
7. Copy the Firebase configuration object

## Step 4: Update Firebase Configuration

1. Open `src/firebase/config.ts` in your project
2. Replace the placeholder values with your actual Firebase configuration:

```typescript
const firebaseConfig = {
  apiKey: "your-actual-api-key",
  authDomain: "your-project-id.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project-id.appspot.com",
  messagingSenderId: "your-messaging-sender-id",
  appId: "your-app-id"
};
```

## Step 5: Install Dependencies

Run the following command in your frontend directory:

```bash
npm install
```

## Step 6: Test the Authentication

1. Start your development server: `npm run dev`
2. Open your browser and navigate to the app
3. Try signing up with a new email and password
4. Try signing in with existing credentials
5. Test Google sign-in

## Features Implemented

### Email/Password Authentication
- User registration with email and password
- User login with existing credentials
- Password confirmation for registration
- Password visibility toggle
- Form validation and error handling

### Google Authentication
- One-click Google sign-in
- Automatic account creation for new Google users
- Seamless integration with existing users

### User Experience
- Persistent authentication state
- Automatic login after page refresh
- User information display in dashboard
- Proper logout functionality
- Loading states and error messages

### Security Features
- Password strength validation
- Secure authentication flow
- Protected routes and components

## Troubleshooting

### Common Issues

1. **"Firebase: Error (auth/unauthorized-domain)"**
   - Add your domain to authorized domains in Firebase Console > Authentication > Settings > Authorized domains

2. **"Firebase: Error (auth/operation-not-allowed)"**
   - Ensure the sign-in method is enabled in Firebase Console > Authentication > Sign-in method

3. **Google Sign-in not working**
   - Check if Google provider is enabled
   - Verify your project support email is set correctly

4. **Build errors**
   - Make sure all dependencies are installed: `npm install`
   - Check TypeScript configuration

### Environment Variables (Optional)

For production, you can use environment variables:

1. Create a `.env` file in your frontend directory
2. Add your Firebase config:

```env
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

3. Update `src/firebase/config.ts`:

```typescript
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};
```

## Next Steps

After setting up Firebase authentication, you can:

1. **Customize the UI**: Modify the login/signup forms to match your brand
2. **Add more providers**: Enable Facebook, Twitter, or other OAuth providers
3. **User profiles**: Store additional user information in Firestore
4. **Role-based access**: Implement different user roles and permissions
5. **Email verification**: Enable email verification for new accounts
6. **Password reset**: Add password reset functionality

## Support

If you encounter any issues:

1. Check the [Firebase Documentation](https://firebase.google.com/docs)
2. Review the [Firebase Authentication Guide](https://firebase.google.com/docs/auth)
3. Check the browser console for error messages
4. Verify your Firebase configuration is correct

## Security Notes

- Never commit your Firebase config with real API keys to version control
- Use environment variables for production deployments
- Enable appropriate security rules in Firebase Console
- Regularly review your Firebase project settings and usage
