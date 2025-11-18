import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import apiService from '../../services/api';

const { width } = Dimensions.get('window');

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<{
    total_voters: number;
    assigned_voters: number;
    visited_voters: number;
    voted_voters: number;
    total_karyakartas: number;
    total_surveys: number;
    karyakarta_performance: Array<any>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await apiService.getDashboard('admin');
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  const handleLogout = () => {
    logout();
    router.replace('/login');
  };

  const handleImport = () => {
    router.push('/(admin)/import');
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      </SafeAreaView>
    );
  }

  const stats = [
    {
      id: 1,
      title: 'Total Voters',
      value: dashboardData?.total_voters || 0,
      icon: 'people',
      color: '#2563EB',
      bgColor: '#DBEAFE',
    },
    {
      id: 2,
      title: 'Assigned',
      value: dashboardData?.assigned_voters || 0,
      icon: 'assignment',
      color: '#8B5CF6',
      bgColor: '#EDE9FE',
    },
    {
      id: 3,
      title: 'Visited',
      value: dashboardData?.visited_voters || 0,
      icon: 'check-circle',
      color: '#10B981',
      bgColor: '#D1FAE5',
    },
    {
      id: 4,
      title: 'Voted',
      value: dashboardData?.voted_voters || 0,
      icon: 'how-to-vote',
      color: '#F59E0B',
      bgColor: '#FEF3C7',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={{ padding: 16 }}>
          <TouchableOpacity
            style={{ backgroundColor: '#2563EB', padding: 10, borderRadius: 8, alignItems: 'center', marginBottom: 12 }}
            onPress={handleImport}
          >
            <Text style={{ color: '#fff', fontWeight: '600' }}>Import Voters (CSV)</Text>
          </TouchableOpacity>
        </View>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Admin Panel</Text>
            <Text style={styles.userName}>{user?.full_name}</Text>
          </View>
          <TouchableOpacity onPress={handleLogout}>
            <MaterialIcons name="logout" size={28} color="#1F2937" />
          </TouchableOpacity>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          {stats.map((stat) => (
            <View key={stat.id} style={styles.statCard}>
              <View style={[styles.statIconContainer, { backgroundColor: stat.bgColor }]}>
                <MaterialIcons name={stat.icon as any} size={24} color={stat.color} />
              </View>
              <Text style={styles.statValue}>{stat.value}</Text>
              <Text style={styles.statTitle}>{stat.title}</Text>
            </View>
          ))}
        </View>

        {/* Team Performance */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Team Performance</Text>
          <View style={styles.card}>
            <View style={styles.performanceRow}>
              <Text style={styles.performanceLabel}>Karyakartas</Text>
              <Text style={styles.performanceValue}>
                {dashboardData?.total_karyakartas || 0}
              </Text>
            </View>
            <View style={styles.performanceRow}>
              <Text style={styles.performanceLabel}>Total Surveys</Text>
              <Text style={styles.performanceValue}>
                {dashboardData?.total_surveys || 0}
              </Text>
            </View>
          </View>
        </View>

        {/* Karyakarta Performance */}
        {dashboardData?.karyakarta_performance && dashboardData.karyakarta_performance.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Karyakarta Performance</Text>
            {dashboardData.karyakarta_performance.map((k: any) => (
              <View key={k.id} style={styles.karyakartaCard}>
                <View style={styles.karyakartaHeader}>
                  <MaterialIcons name="person" size={24} color="#2563EB" />
                  <View style={styles.karyakartaInfo}>
                    <Text style={styles.karyakartaName}>{k.name}</Text>
                    <Text style={styles.karyakartaCoverage}>
                      Coverage: {Math.round(k.coverage)}%
                    </Text>
                  </View>
                </View>
                <View style={styles.karyakartaStats}>
                  <View style={styles.karyakartaStat}>
                    <Text style={styles.karyakartaStatLabel}>Assigned</Text>
                    <Text style={styles.karyakartaStatValue}>{k.assigned_voters}</Text>
                  </View>
                  <View style={styles.karyakartaStat}>
                    <Text style={styles.karyakartaStatLabel}>Visited</Text>
                    <Text style={styles.karyakartaStatValue}>{k.visited_voters}</Text>
                  </View>
                  <View style={styles.karyakartaStat}>
                    <Text style={styles.karyakartaStatLabel}>Surveys</Text>
                    <Text style={styles.karyakartaStatValue}>{k.surveys_completed}</Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
  },
  greeting: {
    fontSize: 14,
    color: '#6B7280',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
  },
  statCard: {
    width: (width - 48) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    margin: 8,
    alignItems: 'center',
  },
  statIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
  },
  performanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  performanceLabel: {
    fontSize: 16,
    color: '#6B7280',
  },
  performanceValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  karyakartaCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  karyakartaHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  karyakartaInfo: {
    marginLeft: 12,
    flex: 1,
  },
  karyakartaName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  karyakartaCoverage: {
    fontSize: 14,
    color: '#10B981',
    marginTop: 2,
  },
  karyakartaStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  karyakartaStat: {
    alignItems: 'center',
  },
  karyakartaStatLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  karyakartaStatValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2563EB',
  },
});
