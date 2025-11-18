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

export default function SuperAdminEDayScreen() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const boothWise = await apiService.getBoothWiseAnalytics();
      const casteDist = await apiService.getCasteDistribution();
      const turnout = await apiService.getLiveTurnout();
      const favorHeatmap = await apiService.getFavorScoreHeatmap();
      setAnalytics({ boothWise, casteDist, turnout, favorHeatmap });
    } catch (error) {
      console.error('Error loading analytics:', error);
      Alert.alert('Error', 'Failed to load analytics');
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
        <Text style={styles.headerTitle}>E-Day Analytics</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#8B5CF6" />
          </View>
        ) : (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Booth-wise Analytics</Text>
              <Text style={styles.sectionValue}>{analytics?.boothWise?.summary || 'N/A'}</Text>
            </View>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Caste Distribution</Text>
              <Text style={styles.sectionValue}>{analytics?.casteDist?.summary || 'N/A'}</Text>
            </View>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Live Turnout</Text>
              <Text style={styles.sectionValue}>{analytics?.turnout?.percentage || 0}%</Text>
            </View>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Favor Score Heatmap</Text>
              <Text style={styles.sectionValue}>{analytics?.favorHeatmap?.summary || 'N/A'}</Text>
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
    color: '#8B5CF6',
    marginBottom: 8,
  },
  sectionValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
});
