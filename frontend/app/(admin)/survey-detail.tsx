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
import { useRouter, useLocalSearchParams } from 'expo-router';
import apiService from '../../services/api';

export default function AdminSurveyDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTemplate();
  }, [params.template_id]);

  const loadTemplate = async () => {
    try {
      if (!params.template_id) return;
      const data = await apiService.getSurveyTemplateById(params.template_id as string);
      setTemplate(data);
    } catch (error) {
      console.error('Error loading template:', error);
      Alert.alert('Error', 'Failed to load survey template');
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

  if (!template) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.emptyState}>
          <MaterialIcons name="assignment" size={64} color="#9CA3AF" />
          <Text style={styles.emptyText}>Survey template not found</Text>
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
        <Text style={styles.headerTitle}>{template.template_name}</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        <Text style={styles.templateDesc}>{template.description}</Text>
        {template.questions.map((question: any) => (
          <View key={question.id} style={styles.questionCard}>
            <Text style={styles.questionText}>
              {question.question_text}
              {question.required && <Text style={styles.required}> *</Text>}
            </Text>
            {question.question_text_marathi && (
              <Text style={styles.questionTextMarathi}>{question.question_text_marathi}</Text>
            )}
            <Text style={styles.questionType}>Type: {question.type}</Text>
            {question.options && question.options.length > 0 && (
              <View style={styles.optionsList}>
                {question.options.map((opt: string) => (
                  <Text key={opt} style={styles.optionItem}>• {opt}</Text>
                ))}
              </View>
            )}
          </View>
        ))}
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
  templateDesc: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12,
  },
  questionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  questionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  questionTextMarathi: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  required: {
    color: '#EF4444',
  },
  questionType: {
    fontSize: 12,
    color: '#2563EB',
    marginBottom: 4,
  },
  optionsList: {
    marginTop: 4,
    marginLeft: 8,
  },
  optionItem: {
    fontSize: 12,
    color: '#6B7280',
  },
});
