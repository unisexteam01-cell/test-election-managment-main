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

export default function SuperAdminDashboard() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await apiService.getDashboard('super-admin');
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

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#8B5CF6" />
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
      title: 'Visited',
      value: dashboardData?.visited_voters || 0,
      icon: 'check-circle',
      color: '#10B981',
      bgColor: '#D1FAE5',
    },
    {
      id: 3,
      title: 'Voted',
      value: dashboardData?.voted_voters || 0,
      icon: 'how-to-vote',
      color: '#F59E0B',
      bgColor: '#FEF3C7',
    },
    {
      id: 4,
      title: 'Surveys',
      value: dashboardData?.total_surveys || 0,
      icon: 'assignment',
      color: '#8B5CF6',
      bgColor: '#EDE9FE',
    },
  ];

  const percentageStats = [
    {
      id: 1,
      title: 'Visit Coverage',
      value: `${Math.round(dashboardData?.visit_percentage || 0)}%`,
      icon: 'trending-up',
      color: '#10B981',
    },
    {
      id: 2,
      title: 'Turnout',
      value: `${Math.round(dashboardData?.turnout_percentage || 0)}%`,
      icon: 'poll',
      color: '#2563EB',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Super Admin</Text>
            <Text style={styles.userName}>{user?.full_name}</Text>
          </View>
          <TouchableOpacity onPress={handleLogout}>
            <MaterialIcons name="logout" size={28} color="#1F2937" />
          </TouchableOpacity>
        </View>

        {/* Main Stats Grid */}
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

        {/* Percentage Stats */}
        <View style={styles.percentageContainer}>
          {percentageStats.map((stat) => (
            <View key={stat.id} style={styles.percentageCard}>
              <MaterialIcons name={stat.icon as any} size={32} color={stat.color} />
              <View style={styles.percentageInfo}>
                <Text style={styles.percentageValue}>{stat.value}</Text>
                <Text style={styles.percentageTitle}>{stat.title}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* System Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Overview</Text>
          <View style={styles.card}>
            <View style={styles.overviewRow}>
              <MaterialIcons name="admin-panel-settings" size={24} color="#8B5CF6" />
              <Text style={styles.overviewLabel}>Total Admins</Text>
              <Text style={styles.overviewValue}>{dashboardData?.total_admins || 0}</Text>
            </View>
            <View style={styles.overviewRow}>
              <MaterialIcons name="people" size={24} color="#2563EB" />
              <Text style={styles.overviewLabel}>Total Karyakartas</Text>
              <Text style={styles.overviewValue}>
                {dashboardData?.total_karyakartas || 0}
              </Text>
            </View>
          </View>
        </View>

        {/* Booth Performance */}
        {dashboardData?.booth_performance && dashboardData.booth_performance.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Top Performing Booths</Text>
            {dashboardData.booth_performance.slice(0, 5).map((booth: any) => (
              <View key={booth._id} style={styles.boothCard}>
                <View style={styles.boothHeader}>
                  <MaterialIcons name="location-on" size={20} color="#6B7280" />
                  <Text style={styles.boothNumber}>Booth {booth._id}</Text>
                </View>
                <View style={styles.boothStats}>
                  <View style={styles.boothStat}>
                    <Text style={styles.boothStatLabel}>Total</Text>
                    <Text style={styles.boothStatValue}>{booth.total}</Text>
                  </View>
                  <View style={styles.boothStat}>
                    <Text style={styles.boothStatLabel}>Visited</Text>
                    <Text style={styles.boothStatValue}>{booth.visited}</Text>
                  </View>
                  <View style={styles.boothStat}>
                    <Text style={styles.boothStatLabel}>Voted</Text>
                    <Text style={styles.boothStatValue}>{booth.voted}</Text>
                  </View>
                  <View style={styles.boothStat}>
                    <Text style={styles.boothStatLabel}>Turnout</Text>
                    <Text style={styles.boothStatValue}>
                      {Math.round((booth.voted / booth.total) * 100)}%
                    </Text>
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
  percentageContainer: {
    padding: 16,
    gap: 12,
  },
  percentageCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    gap: 16,
  },
  percentageInfo: {
    flex: 1,
  },
  percentageValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  percentageTitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
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
  overviewRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
    gap: 12,
  },
  overviewLabel: {
    flex: 1,
    fontSize: 16,
    color: '#6B7280',
  },
  overviewValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  boothCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  boothHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  boothNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  boothStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  boothStat: {
    alignItems: 'center',
  },
  boothStatLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  boothStatValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2563EB',
  },
});
