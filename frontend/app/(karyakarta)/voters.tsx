import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import apiService from '../../services/api';

export default function VotersScreen() {
  const router = useRouter();
  const [voters, setVoters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadVoters();
  }, [page, search]);

  const loadVoters = async () => {
    try {
      setLoading(true);
      const response = await apiService.getVoters({
        page,
        limit: 20,
        search: search || undefined,
      });
      setVoters(response.voters);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Error loading voters:', error);
      Alert.alert('Error', 'Failed to load voters');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    setPage(1);
    loadVoters();
  };

  const markVisited = async (voterId: string) => {
    try {
      await apiService.markVoterVisited(voterId);
      Alert.alert('Success', 'Voter marked as visited');
      loadVoters();
    } catch (error) {
      Alert.alert('Error', 'Failed to mark voter as visited');
    }
  };

  const markVoted = async (voterId: string) => {
    try {
      await apiService.markVoterVoted(voterId);
      Alert.alert('Success', 'Voter marked as voted');
      loadVoters();
    } catch (error) {
      Alert.alert('Error', 'Failed to mark voter as voted');
    }
  };

  const renderVoter = ({ item }: any) => (
    <View style={styles.voterCard}>
      <View style={styles.voterHeader}>
        <View style={styles.voterInfo}>
          <Text style={styles.voterName}>{item.full_name}</Text>
          <View style={styles.voterDetails}>
            <MaterialIcons name="location-on" size={14} color="#6B7280" />
            <Text style={styles.detailText}>{item.area}</Text>
          </View>
          <View style={styles.voterDetails}>
            <MaterialIcons name="how-to-vote" size={14} color="#6B7280" />
            <Text style={styles.detailText}>Booth: {item.booth_number}</Text>
          </View>
        </View>
        <View style={styles.badges}>
          {item.visited_status && (
            <View style={[styles.badge, styles.visitedBadge]}>
              <MaterialIcons name="check" size={14} color="#10B981" />
            </View>
          )}
          {item.voted_status && (
            <View style={[styles.badge, styles.votedBadge]}>
              <MaterialIcons name="how-to-vote" size={14} color="#2563EB" />
            </View>
          )}
        </View>
      </View>

      <View style={styles.actions}>
        {!item.visited_status && (
          <TouchableOpacity
            style={[styles.actionButton, styles.visitButton]}
            onPress={() => markVisited(item._id)}
          >
            <MaterialIcons name="check-circle" size={18} color="#FFFFFF" />
            <Text style={styles.actionButtonText}>Mark Visited</Text>
          </TouchableOpacity>
        )}
        {!item.voted_status && (
          <TouchableOpacity
            style={[styles.actionButton, styles.voteButton]}
            onPress={() => markVoted(item._id)}
          >
            <MaterialIcons name="how-to-vote" size={18} color="#FFFFFF" />
            <Text style={styles.actionButtonText}>Mark Voted</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.searchContainer}>
        <MaterialIcons name="search" size={24} color="#6B7280" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search by name, phone, address..."
          value={search}
          onChangeText={setSearch}
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {loading && page === 1 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      ) : (
        <FlatList
          data={voters}
          renderItem={renderVoter}
          keyExtractor={(item) => item._id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <MaterialIcons name="people" size={64} color="#9CA3AF" />
              <Text style={styles.emptyText}>No voters found</Text>
            </View>
          }
        />
      )}

      <View style={styles.pagination}>
        <TouchableOpacity
          style={[styles.pageButton, page === 1 && styles.pageButtonDisabled]}
          onPress={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
        >
          <MaterialIcons name="chevron-left" size={24} color={page === 1 ? '#9CA3AF' : '#2563EB'} />
        </TouchableOpacity>
        <Text style={styles.pageText}>
          Page {page} of {totalPages}
        </Text>
        <TouchableOpacity
          style={[styles.pageButton, page === totalPages && styles.pageButtonDisabled]}
          onPress={() => setPage(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
        >
          <MaterialIcons name="chevron-right" size={24} color={page === totalPages ? '#9CA3AF' : '#2563EB'} />
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
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 48,
    fontSize: 16,
    color: '#1F2937',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    padding: 16,
  },
  voterCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  voterHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  voterInfo: {
    flex: 1,
  },
  voterName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  voterDetails: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  detailText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 4,
  },
  badges: {
    flexDirection: 'row',
    gap: 8,
  },
  badge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  visitedBadge: {
    backgroundColor: '#D1FAE5',
  },
  votedBadge: {
    backgroundColor: '#DBEAFE',
  },
  actions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 8,
    gap: 4,
  },
  visitButton: {
    backgroundColor: '#10B981',
  },
  voteButton: {
    backgroundColor: '#2563EB',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 16,
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  pageButton: {
    padding: 8,
  },
  pageButtonDisabled: {
    opacity: 0.5,
  },
  pageText: {
    fontSize: 14,
    color: '#1F2937',
    marginHorizontal: 16,
  },
});
