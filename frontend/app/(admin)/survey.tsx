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

export default function AdminSurveyScreen() {
  const router = useRouter();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await apiService.getSurveyTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Error loading templates:', error);
      Alert.alert('Error', 'Failed to load survey templates');
    } finally {
      setLoading(false);
    }
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

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <MaterialIcons name="arrow-back" size={24} color="#1F2937" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Survey Templates</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {templates.length === 0 ? (
          <View style={styles.emptyState}>
            <MaterialIcons name="assignment" size={64} color="#9CA3AF" />
            <Text style={styles.emptyText}>No survey templates available</Text>
          </View>
        ) : (
          templates.map((template: any) => (
            <View key={template._id} style={styles.templateCard}>
              <Text style={styles.templateName}>{template.template_name}</Text>
              <Text style={styles.templateDesc}>{template.description}</Text>
              <TouchableOpacity
                style={styles.viewButton}
                onPress={() => router.push({ pathname: '/admin/survey-detail', params: { template_id: template._id } })}
              >
                <Text style={styles.viewButtonText}>View Details</Text>
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
  templateCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  templateName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  templateDesc: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12,
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
