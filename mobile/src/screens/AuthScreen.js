import React, { useState } from 'react';
import {
  View, Text, TouchableOpacity, TextInput, StyleSheet,
  ScrollView, ActivityIndicator, Alert, KeyboardAvoidingView, Platform
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

// Theme colors
const T = {
  bg: '#050810',
  card: '#0a1128',
  cardBorder: '#1a2744',
  text: '#f0f4ff',
  textMuted: '#8896b8',
  primary: '#3b82f6',
  primaryGlow: 'rgba(59, 130, 246, 0.1)',
  success: '#10b981',
  danger: '#ef4444',
  white: '#ffffff',
};

// API configuration
const API_URLS = [
  'https://www.zurixsciences.com/api',
  'https://zurixsciences.com/api',
];

const fetchAPI = async (endpoint, options = {}) => {
  let lastError = null;
  
  for (const baseUrl of API_URLS) {
    try {
      const response = await fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
      }
      
      return data;
    } catch (error) {
      lastError = error;
    }
  }
  
  throw lastError || new Error('All API endpoints failed');
};

export default function AuthScreen({ onLogin, onSkip }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetchAPI('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      if (response.success) {
        onLogin(response.token, response.user);
      }
    } catch (error) {
      Alert.alert('Login Failed', error.message || 'Invalid email or password');
    }
    setLoading(false);
  };

  const handleRegister = async () => {
    if (!email || !password || !name) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      const response = await fetchAPI('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password, name }),
      });

      if (response.success) {
        onLogin(response.token, response.user);
      }
    } catch (error) {
      Alert.alert('Registration Failed', error.message || 'Could not create account');
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <LinearGradient
              colors={['#3b82f6', '#8b5cf6']}
              style={styles.logoContainer}
            >
              <Ionicons name="flask" size={40} color={T.white} />
            </LinearGradient>
            <Text style={styles.title}>Zurix Sciences</Text>
            <Text style={styles.subtitle}>
              {mode === 'login' ? 'Welcome back' : 'Create your account'}
            </Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            {mode === 'register' && (
              <View style={styles.inputContainer}>
                <Text style={styles.label}>NAME</Text>
                <View style={styles.inputWrapper}>
                  <Ionicons name="person-outline" size={20} color={T.textMuted} />
                  <TextInput
                    style={styles.input}
                    placeholder="Your name"
                    placeholderTextColor={T.textMuted}
                    value={name}
                    onChangeText={setName}
                    autoCapitalize="words"
                  />
                </View>
              </View>
            )}

            <View style={styles.inputContainer}>
              <Text style={styles.label}>EMAIL</Text>
              <View style={styles.inputWrapper}>
                <Ionicons name="mail-outline" size={20} color={T.textMuted} />
                <TextInput
                  style={styles.input}
                  placeholder="your@email.com"
                  placeholderTextColor={T.textMuted}
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>PASSWORD</Text>
              <View style={styles.inputWrapper}>
                <Ionicons name="lock-closed-outline" size={20} color={T.textMuted} />
                <TextInput
                  style={styles.input}
                  placeholder="Your password"
                  placeholderTextColor={T.textMuted}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry={!showPassword}
                />
                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                  <Ionicons 
                    name={showPassword ? "eye-off-outline" : "eye-outline"} 
                    size={20} 
                    color={T.textMuted} 
                  />
                </TouchableOpacity>
              </View>
            </View>

            {/* Submit Button */}
            <TouchableOpacity
              style={styles.submitButton}
              onPress={mode === 'login' ? handleLogin : handleRegister}
              disabled={loading}
            >
              <LinearGradient
                colors={['#3b82f6', '#8b5cf6']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.submitButtonGradient}
              >
                {loading ? (
                  <ActivityIndicator color={T.white} />
                ) : (
                  <>
                    <Text style={styles.submitButtonText}>
                      {mode === 'login' ? 'Sign In' : 'Create Account'}
                    </Text>
                    <Ionicons name="arrow-forward" size={20} color={T.white} />
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>

            {/* Switch Mode */}
            <TouchableOpacity
              style={styles.switchMode}
              onPress={() => setMode(mode === 'login' ? 'register' : 'login')}
            >
              <Text style={styles.switchModeText}>
                {mode === 'login' 
                  ? "Don't have an account? " 
                  : "Already have an account? "}
                <Text style={styles.switchModeLink}>
                  {mode === 'login' ? 'Sign Up' : 'Sign In'}
                </Text>
              </Text>
            </TouchableOpacity>

            {/* Skip Button */}
            <TouchableOpacity style={styles.skipButton} onPress={onSkip}>
              <Text style={styles.skipButtonText}>Continue without account</Text>
            </TouchableOpacity>
          </View>

          {/* Footer */}
          <Text style={styles.footer}>
            By continuing, you agree to our Terms of Service
          </Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: T.bg,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: T.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: T.textMuted,
  },
  form: {
    marginBottom: 24,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 12,
    fontWeight: '700',
    color: T.textMuted,
    letterSpacing: 1,
    marginBottom: 10,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: T.card,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: T.cardBorder,
    paddingHorizontal: 16,
    gap: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: T.text,
    paddingVertical: 16,
  },
  submitButton: {
    borderRadius: 14,
    overflow: 'hidden',
    marginTop: 10,
  },
  submitButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 10,
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: T.white,
  },
  switchMode: {
    alignItems: 'center',
    marginTop: 24,
  },
  switchModeText: {
    fontSize: 14,
    color: T.textMuted,
  },
  switchModeLink: {
    color: T.primary,
    fontWeight: '600',
  },
  skipButton: {
    alignItems: 'center',
    marginTop: 20,
    padding: 12,
  },
  skipButtonText: {
    fontSize: 14,
    color: T.textMuted,
  },
  footer: {
    fontSize: 12,
    color: T.textMuted,
    textAlign: 'center',
  },
});
