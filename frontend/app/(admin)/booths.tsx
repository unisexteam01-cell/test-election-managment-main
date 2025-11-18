import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import apiService from '../../services/api';

export default function BoothsScreen() {
  const router = useRouter();
  const [booths, setBooths] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBooths();
  }, []);

  const loadBooths = async () => {
    try {
      const data = await apiService.getBoothPerformance();
      setBooths(data);
    } catch (error) {
      console.error('Error loading booths:', error);
      Alert.alert('Error', 'Failed to load booths');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <MaterialIcons name="arrow-back" size={24} color="#1F2937" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Booths</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#2563EB" />
          </View>
        ) : booths.length === 0 ? (
          <View style={styles.emptyState}>
            <MaterialIcons name="location-on" size={64} color="#9CA3AF" />
            <Text style={styles.emptyText}>No booths found</Text>
          </View>
        ) : (
          booths.map((booth: any) => (
            <View key={booth._id} style={styles.boothCard}>
              <Text style={styles.boothName}>Booth {booth._id}</Text>
              <Text style={styles.boothStat}>Visited: {booth.visited}</Text>
              <Text style={styles.boothStat}>Voted: {booth.voted}</Text>
              <Text style={styles.boothStat}>Turnout: {Math.round((booth.voted / booth.total) * 100)}%</Text>
            </View>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 16,
  },
  boothCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  boothName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  boothStat: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
});
