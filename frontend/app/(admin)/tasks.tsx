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

export default function AdminTasksScreen() {
  const router = useRouter();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await apiService.getMyTasks();
      setTasks(data);
    } catch (error) {
      console.error('Error loading tasks:', error);
      Alert.alert('Error', 'Failed to load tasks');
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
        <Text style={styles.headerTitle}>Assigned Tasks</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#2563EB" />
          </View>
        ) : tasks.length === 0 ? (
          <View style={styles.emptyState}>
            <MaterialIcons name="assignment" size={64} color="#9CA3AF" />
            <Text style={styles.emptyText}>No tasks assigned</Text>
          </View>
        ) : (
          tasks.map((task: any) => (
            <View key={task._id} style={styles.taskCard}>
              <Text style={styles.taskTitle}>{task.title}</Text>
              <Text style={styles.taskDesc}>{task.description}</Text>
              <Text style={styles.taskStatus}>Status: {task.status}</Text>
              <TouchableOpacity
                style={styles.updateButton}
                onPress={() => router.push({ pathname: '/admin/task-detail', params: { task_id: task._id } })}
              >
                <Text style={styles.updateButtonText}>View / Update</Text>
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
  taskCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  taskDesc: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  taskStatus: {
    fontSize: 12,
    color: '#2563EB',
    marginBottom: 8,
  },
  updateButton: {
    backgroundColor: '#2563EB',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  updateButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
