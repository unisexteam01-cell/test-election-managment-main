import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import apiService from '../../services/api';
import * as Location from 'expo-location';

export default function SurveyScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [location, setLocation] = useState(null);

  useEffect(() => {
    loadTemplates();
    getLocationPermission();
  }, []);

  const getLocationPermission = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status === 'granted') {
      const loc = await Location.getCurrentPositionAsync({});
      setLocation(loc.coords);
    }
  };

  const loadTemplates = async () => {
    try {
      const data = await apiService.getSurveyTemplates();
      setTemplates(data);
      if (data.length > 0) {
        setSelectedTemplate(data[0]);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
      Alert.alert('Error', 'Failed to load survey templates');
    } finally {
      setLoading(false);
    }
  };

  const handleResponse = (questionId: string, answer: any) => {
    setResponses({ ...responses, [questionId]: answer });
  };

  const submitSurvey = async () => {
    if (!selectedTemplate) return;

    // Validate required fields
    const requiredQuestions = selectedTemplate.questions.filter(q => q.required);
    const missingResponses = requiredQuestions.filter(q => !responses[q.id]);

    if (missingResponses.length > 0) {
      Alert.alert('Error', 'Please answer all required questions');
      return;
    }

    if (!params.voter_id) {
      Alert.alert('Error', 'Voter ID is required');
      return;
    }

    setSubmitting(true);
    try {
      const surveyData = {
        voter_id: params.voter_id as string,
        template_id: selectedTemplate._id,
        responses: Object.entries(responses).map(([question_id, answer]) => ({
          question_id,
          answer,
        })),
        gps_location: location
          ? { latitude: location.latitude, longitude: location.longitude }
          : undefined,
        photos: [],
        audio_notes: [],
      };

      await apiService.submitSurvey(surveyData);
      Alert.alert('Success', 'Survey submitted successfully', [
        { text: 'OK', onPress: () => router.back() },
      ]);
    } catch (error) {
      console.error('Error submitting survey:', error);
      Alert.alert('Error', 'Failed to submit survey');
    } finally {
      setSubmitting(false);
    }
  };

  const renderQuestion = (question: any) => {
    switch (question.type) {
      case 'yesno':
        return (
          <View style={styles.questionOptions}>
            <TouchableOpacity
              style={[
                styles.optionButton,
                responses[question.id] === 'yes' && styles.optionButtonSelected,
              ]}
              onPress={() => handleResponse(question.id, 'yes')}
            >
              <Text
                style={[
                  styles.optionText,
                  responses[question.id] === 'yes' && styles.optionTextSelected,
                ]}
              >
                Yes
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.optionButton,
                responses[question.id] === 'no' && styles.optionButtonSelected,
              ]}
              onPress={() => handleResponse(question.id, 'no')}
            >
              <Text
                style={[
                  styles.optionText,
                  responses[question.id] === 'no' && styles.optionTextSelected,
                ]}
              >
                No
              </Text>
            </TouchableOpacity>
          </View>
        );

      case 'mcq':
        return (
          <View style={styles.questionOptions}>
            {question.options.map((option: string) => (
              <TouchableOpacity
                key={option}
                style={[
                  styles.optionButton,
                  responses[question.id] === option && styles.optionButtonSelected,
                ]}
                onPress={() => handleResponse(question.id, option)}
              >
                <Text
                  style={[
                    styles.optionText,
                    responses[question.id] === option && styles.optionTextSelected,
                  ]}
                >
                  {option}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        );

      case 'rating':
        return (
          <View style={styles.ratingContainer}>
            {[1, 2, 3, 4, 5].map((rating) => (
              <TouchableOpacity
                key={rating}
                onPress={() => handleResponse(question.id, rating)}
              >
                <MaterialIcons
                  name={responses[question.id] >= rating ? 'star' : 'star-border'}
                  size={40}
                  color="#F59E0B"
                />
              </TouchableOpacity>
            ))}
          </View>
        );

      case 'text':
      case 'phone':
      case 'number':
        return (
          <TextInput
            style={styles.textInput}
            value={responses[question.id] || ''}
            onChangeText={(text) => handleResponse(question.id, text)}
            placeholder="Enter your answer"
            keyboardType={question.type === 'phone' || question.type === 'number' ? 'numeric' : 'default'}
          />
        );

      default:
        return null;
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

  if (!selectedTemplate) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.emptyState}>
          <MaterialIcons name="assignment" size={64} color="#9CA3AF" />
          <Text style={styles.emptyText}>No survey templates available</Text>
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
        <Text style={styles.headerTitle}>{selectedTemplate.template_name}</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content}>
        {selectedTemplate.questions.map((question: any) => (
          <View key={question.id} style={styles.questionCard}>
            <Text style={styles.questionText}>
              {question.question_text}
              {question.required && <Text style={styles.required}> *</Text>}
            </Text>
            {question.question_text_marathi && (
              <Text style={styles.questionTextMarathi}>{question.question_text_marathi}</Text>
            )}
            {renderQuestion(question)}
          </View>
        ))}

        {location && (
          <View style={styles.locationInfo}>
            <MaterialIcons name="location-on" size={20} color="#10B981" />
            <Text style={styles.locationText}>
              Location captured: {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
            </Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.submitButton, submitting && styles.submitButtonDisabled]}
          onPress={submitSurvey}
          disabled={submitting}
        >
          {submitting ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <>
              <MaterialIcons name="send" size={20} color="#FFFFFF" />
              <Text style={styles.submitButtonText}>Submit Survey</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
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
    marginBottom: 12,
  },
  required: {
    color: '#EF4444',
  },
  questionOptions: {
    gap: 8,
  },
  optionButton: {
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  optionButtonSelected: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  optionText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  optionTextSelected: {
    color: '#2563EB',
    fontWeight: '600',
  },
  ratingContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#1F2937',
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
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 16,
  },
  locationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#D1FAE5',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  locationText: {
    fontSize: 12,
    color: '#065F46',
    marginLeft: 8,
  },
  footer: {
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2563EB',
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
