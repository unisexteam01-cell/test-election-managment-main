import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function SuperAdminDashboard() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Super Admin Dashboard</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 20, fontWeight: 'bold' },
});
