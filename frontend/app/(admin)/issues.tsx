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

export default function IssuesScreen() {
  const router = useRouter();
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIssues();
  }, []);

  const loadIssues = async () => {
    try {
      const data = await apiService.getIssues();
      setIssues(data);
    } catch (error) {
      console.error('Error loading issues:', error);
      Alert.alert('Error', 'Failed to load issues');
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
        <Text style={styles.headerTitle}>Issues</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#2563EB" />
          </View>
        ) : issues.length === 0 ? (
          <View style={styles.emptyState}>
            <MaterialIcons name="report-problem" size={64} color="#9CA3AF" />
            <Text style={styles.emptyText}>No issues found</Text>
          </View>
        ) : (
          issues.map((issue: any) => (
            <View key={issue._id} style={styles.issueCard}>
              <Text style={styles.issueTitle}>{issue.title}</Text>
              <Text style={styles.issueStatus}>Status: {issue.status}</Text>
              <TouchableOpacity
                style={styles.viewButton}
                onPress={() => router.push({ pathname: '/admin/issue-detail', params: { issue_id: issue._id } })}
              >
                <Text style={styles.viewButtonText}>View / Resolve</Text>
              </TouchableOpacity>
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
  issueCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  issueTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  issueStatus: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  viewButton: {
    backgroundColor: '#2563EB',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  viewButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
