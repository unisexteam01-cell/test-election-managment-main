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

export default function AdminEDayScreen() {
  const router = useRouter();
  const [turnout, setTurnout] = useState(null);
  const [boothPerformance, setBoothPerformance] = useState([]);
  const [favorScore, setFavorScore] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEDayData();
  }, []);

  const loadEDayData = async () => {
    try {
      const turnoutData = await apiService.getLiveTurnout();
      const boothData = await apiService.getBoothPerformance();
      const favorData = await apiService.getFavorScoreTrends();
      setTurnout(turnoutData);
      setBoothPerformance(boothData);
      setFavorScore(favorData);
    } catch (error) {
      console.error('Error loading E-day data:', error);
      Alert.alert('Error', 'Failed to load E-day data');
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
        <Text style={styles.headerTitle}>E-Day Operations</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#2563EB" />
          </View>
        ) : (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Live Turnout</Text>
              <Text style={styles.sectionValue}>{turnout?.percentage || 0}%</Text>
            </View>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Booth Performance</Text>
              {boothPerformance.map((booth: any) => (
                <View key={booth._id} style={styles.boothCard}>
                  <Text style={styles.boothTitle}>Booth {booth._id}</Text>
                  <Text style={styles.boothStat}>Visited: {booth.visited}</Text>
                  <Text style={styles.boothStat}>Voted: {booth.voted}</Text>
                  <Text style={styles.boothStat}>Turnout: {Math.round((booth.voted / booth.total) * 100)}%</Text>
                </View>
              ))}
            </View>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Favor Score Trends</Text>
              <Text style={styles.sectionValue}>{favorScore?.trend || 'N/A'}</Text>
            </View>
          </>
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
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2563EB',
    marginBottom: 8,
  },
  sectionValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  boothCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  boothTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  boothStat: {
    fontSize: 14,
    color: '#6B7280',
  },
});
