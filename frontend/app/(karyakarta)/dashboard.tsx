import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';

const { width } = Dimensions.get('window');

export default function KaryakartaDashboard() {
  const { user } = useAuth();

  const [dashboardData, setDashboardData] = React.useState({
    assigned_voters: 0,
    visited_voters: 0,
    voted_voters: 0,
    coverage_percentage: 0,
    total_surveys: 0,
    pending_tasks: 0,
    today_surveys: 0,
    today_visits: 0,
  });
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await apiService.getDashboard('karyakarta');
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      id: 1,
      title: 'Assigned Voters',
      value: dashboardData.assigned_voters.toString(),
      icon: 'people',
      color: '#2563EB',
      bgColor: '#DBEAFE',
    },
    {
      id: 2,
      title: 'Visited',
      value: dashboardData.visited_voters.toString(),
      icon: 'check-circle',
      color: '#10B981',
      bgColor: '#D1FAE5',
    },
    {
      id: 3,
      title: 'Surveys',
      value: dashboardData.total_surveys.toString(),
      icon: 'assignment',
      color: '#F59E0B',
      bgColor: '#FEF3C7',
    },
    {
      id: 4,
      title: 'Coverage',
      value: `${Math.round(dashboardData.coverage_percentage)}%`,
      icon: 'trending-up',
      color: '#8B5CF6',
      bgColor: '#EDE9FE',
    },
  ];

  const quickActions = [
    {
      id: 1,
      title: 'Record Survey',
      icon: 'add-circle',
      color: '#2563EB',
    },
    {
      id: 2,
      title: 'Find Voter',
      icon: 'search',
      color: '#10B981',
    },
    {
      id: 3,
      title: 'Mark Voted',
      icon: 'how-to-vote',
      color: '#F59E0B',
    },
    {
      id: 4,
      title: 'View Tasks',
      icon: 'list',
      color: '#EF4444',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome back,</Text>
            <Text style={styles.userName}>{user?.full_name || 'Karyakarta'}</Text>
          </View>
          <MaterialIcons name="notifications" size={28} color="#1F2937" />
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

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionsGrid}>
            {quickActions.map((action) => (
              <TouchableOpacity key={action.id} style={styles.actionCard}>
                <MaterialIcons name={action.icon as any} size={32} color={action.color} />
                <Text style={styles.actionTitle}>{action.title}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Today's Tasks */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Today's Tasks</Text>
          <View style={styles.emptyState}>
            <MaterialIcons name="inbox" size={48} color="#9CA3AF" />
            <Text style={styles.emptyText}>No tasks for today</Text>
            <Text style={styles.emptySubtext}>All caught up! Check back later.</Text>
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <View style={styles.emptyState}>
            <MaterialIcons name="history" size={48} color="#9CA3AF" />
            <Text style={styles.emptyText}>No recent activity</Text>
            <Text style={styles.emptySubtext}>Start by visiting voters or recording surveys</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  scrollView: {
    flex: 1,
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
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -8,
  },
  actionCard: {
    width: (width - 64) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    margin: 8,
    alignItems: 'center',
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginTop: 12,
    textAlign: 'center',
  },
  emptyState: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 12,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 4,
    textAlign: 'center',
  },
});
