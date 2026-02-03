import axios from 'axios';
import { API_URL } from '../constants/config';
import AsyncStorage from '@react-native-async-storage/async-storage';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Products
export const getProducts = async () => {
  const response = await api.get('/products');
  return response.data;
};

export const getProductById = async (id) => {
  const response = await api.get(`/products/${id}`);
  return response.data;
};

// Protocols
export const getProtocols = async (category = null) => {
  const url = category ? `/protocols?category=${category}` : '/protocols';
  const response = await api.get(url);
  return response.data;
};

export const getProtocolById = async (id) => {
  const response = await api.get(`/protocols/${id}`);
  return response.data;
};

// Verification
export const verifyScan = async (code, deviceId) => {
  const response = await api.post('/verify-scan', {
    code,
    device_id: deviceId
  });
  return response.data;
};

export const getVerificationHistory = async (deviceId) => {
  const response = await api.get('/verification-history', {
    params: { device_id: deviceId }
  });
  return response.data;
};

export const getBatchStats = async (batchNumber) => {
  const response = await api.get(`/batch-stats/${batchNumber}`);
  return response.data;
};

// Local Storage for purchased protocols
export const savePurchasedProtocol = async (protocolId) => {
  try {
    const purchased = await AsyncStorage.getItem('purchased_protocols');
    const protocols = purchased ? JSON.parse(purchased) : [];
    if (!protocols.includes(protocolId)) {
      protocols.push(protocolId);
      await AsyncStorage.setItem('purchased_protocols', JSON.stringify(protocols));
    }
    return true;
  } catch (error) {
    console.error('Error saving purchased protocol:', error);
    return false;
  }
};

export const getPurchasedProtocols = async () => {
  try {
    const purchased = await AsyncStorage.getItem('purchased_protocols');
    return purchased ? JSON.parse(purchased) : [];
  } catch (error) {
    console.error('Error getting purchased protocols:', error);
    return [];
  }
};

// Save verification to local history
export const saveVerificationToLocal = async (verification) => {
  try {
    const history = await AsyncStorage.getItem('verification_history');
    const verifications = history ? JSON.parse(history) : [];
    verifications.unshift(verification);
    // Keep only last 50
    if (verifications.length > 50) {
      verifications.pop();
    }
    await AsyncStorage.setItem('verification_history', JSON.stringify(verifications));
    return true;
  } catch (error) {
    console.error('Error saving verification:', error);
    return false;
  }
};

export const getLocalVerificationHistory = async () => {
  try {
    const history = await AsyncStorage.getItem('verification_history');
    return history ? JSON.parse(history) : [];
  } catch (error) {
    console.error('Error getting verification history:', error);
    return [];
  }
};

export default api;
