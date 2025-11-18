import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/auth/login');
          },
        },
      ]
    );
  };

  const menuItems = [
    {
      id: 1,
      title: 'Edit Profile',
      icon: 'edit',
      onPress: () => Alert.alert('Coming Soon', 'Edit profile feature'),
    },
    {
      id: 2,
      title: 'Change Password',
      icon: 'lock',
      onPress: () => Alert.alert('Coming Soon', 'Change password feature'),
    },
    {
      id: 3,
      title: 'Settings',
      icon: 'settings',
      onPress: () => Alert.alert('Coming Soon', 'Settings feature'),
    },
    {
      id: 4,
      title: 'Help & Support',
      icon: 'help',
      onPress: () => Alert.alert('Coming Soon', 'Help & support feature'),
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Profile Header */}
        <View style={styles.profileHeader}>
          <View style={styles.avatarContainer}>
            <MaterialIcons name="person" size={48} color="#FFFFFF" />
          </View>
          <Text style={styles.name}>{user?.full_name || 'User'}</Text>
          <Text style={styles.username}>@{user?.username}</Text>
          <Text style={styles.role}>
            {user?.role === 'karyakarta' ? 'Karyakarta' : user?.role}
          </Text>
        </View>

        {/* Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>
              {user?.activity_stats?.surveys_completed || 0}
            </Text>
            <Text style={styles.statLabel}>Surveys</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>
              {user?.activity_stats?.voters_visited || 0}
            </Text>
            <Text style={styles.statLabel}>Visited</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>
              {user?.activity_stats?.coverage_percentage || 0}%
            </Text>
            <Text style={styles.statLabel}>Coverage</Text>
          </View>
        </View>

        {/* Menu Items */}
        <View style={styles.menuContainer}>
          {menuItems.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={styles.menuItem}
              onPress={item.onPress}
            >
              <View style={styles.menuItemLeft}>
                <MaterialIcons name={item.icon as any} size={24} color="#6B7280" />
                <Text style={styles.menuItemText}>{item.title}</Text>
              </View>
              <MaterialIcons name="chevron-right" size={24} color="#9CA3AF" />
            </TouchableOpacity>
          ))}
        </View>

        {/* Logout Button */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <MaterialIcons name="logout" size={24} color="#EF4444" />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
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
  profileHeader: {
    backgroundColor: '#FFFFFF',
    padding: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  avatarContainer: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  username: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 4,
  },
  role: {
    fontSize: 14,
    color: '#2563EB',
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    padding: 24,
    marginTop: 16,
    borderRadius: 12,
    marginHorizontal: 16,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statDivider: {
    width: 1,
    backgroundColor: '#E5E7EB',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  menuContainer: {
    backgroundColor: '#FFFFFF',
    marginTop: 16,
    marginHorizontal: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuItemText: {
    fontSize: 16,
    color: '#1F2937',
    marginLeft: 12,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    marginTop: 16,
    marginHorizontal: 16,
    marginBottom: 24,
    padding: 16,
    borderRadius: 12,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#EF4444',
    marginLeft: 8,
  },
});
