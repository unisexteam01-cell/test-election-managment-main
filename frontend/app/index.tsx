import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';

export default function Index() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.replace('/auth/login');
      } else {
        switch (user.role) {
          case 'super_admin':
            router.replace('/super-admin/dashboard');
            break;
          case 'admin':
            router.replace('/admin/dashboard');
            break;
          case 'karyakarta':
            router.replace('/karyakarta/dashboard');
            break;
          default:
            router.replace('/auth/login');
        }
      }
    }
  }, [user, loading]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#2563EB" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
