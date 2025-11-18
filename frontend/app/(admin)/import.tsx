import React, { useState, useRef } from 'react';
import { View, Text, Button, Platform, TextInput, StyleSheet, TouchableOpacity, FlatList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import apiService from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';

export default function ImportScreen() {
  const { user } = useAuth();
  const router = useRouter();
  const [preview, setPreview] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [mapping, setMapping] = useState<any>({
    name_english: '',
    name_marathi: '',
    age: '',
    gender: '',
    area_english: '',
    area_marathi: '',
    booth_number: '',
    ward: '',
    phone: '',
    caste: '',
    address: '',
  });
  const [pasteCsv, setPasteCsv] = useState('');
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const onSelectFileWeb = (e: any) => {
    const file = e.target.files[0];
    if (!file) return;
    apiService.uploadCsv(file).then((res) => {
      setColumns(res.columns || []);
      setPreview(res.preview || []);
      setSessionId(res.session_id);
    }).catch(err => alert('Upload failed: ' + err.message));
  };

  const onUploadPaste = async () => {
    // Convert pasted CSV into a Blob and upload
    const blob = new Blob([pasteCsv], { type: 'text/csv' });
    // @ts-ignore
    const file = new File([blob], 'pasted.csv', { type: 'text/csv' });
    try {
      const res = await apiService.uploadCsv(file);
      setColumns(res.columns || []);
      setPreview(res.preview || []);
      setSessionId(res.session_id);
    } catch (e: any) {
      alert('Upload failed: ' + (e.message || e));
    }
  };

  const onMapAndImport = async () => {
    if (!sessionId) return alert('No import session');
    try {
      const res = await apiService.mapColumns(sessionId, mapping, user?.id || user?._id);
      alert(`Import completed: ${res.imported_count} imported, ${res.error_count} errors`);
      router.replace('/admin/dashboard');
    } catch (e: any) {
      alert('Mapping failed: ' + (e.message || e));
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Import Voters (CSV)</Text>

        {Platform.OS === 'web' ? (
          <div>
            <input ref={fileInputRef as any} type="file" accept=".csv,.xlsx" onChange={onSelectFileWeb} />
          </div>
        ) : (
          <View>
            <Text>Paste CSV content below (mobile fallback):</Text>
            <TextInput value={pasteCsv} onChangeText={setPasteCsv} multiline style={styles.pasteBox} />
            <Button title="Upload pasted CSV" onPress={onUploadPaste} />
          </View>
        )}

        {columns.length > 0 && (
          <View style={styles.mapping}>
            <Text style={styles.subtitle}>Column Mapping</Text>
            {[
              { key: 'name_english', label: 'Name (English)' },
              { key: 'name_marathi', label: 'Name (Marathi)' },
              { key: 'age', label: 'Age' },
              { key: 'gender', label: 'Gender' },
              { key: 'area_english', label: 'Area (English)' },
              { key: 'area_marathi', label: 'Area (Marathi)' },
              { key: 'booth_number', label: 'Booth' },
              { key: 'ward', label: 'Ward' },
              { key: 'phone', label: 'Phone' },
              { key: 'caste', label: 'Caste' },
              { key: 'address', label: 'Address' },
            ].map((m) => (
              <View key={m.key} style={styles.mapRow}>
                <Text style={styles.mapLabel}>{m.label}</Text>
                <TextInput
                  style={styles.mapInput}
                  value={mapping[m.key]}
                  onChangeText={(t) => setMapping({ ...mapping, [m.key]: t })}
                  placeholder={columns.join(', ')}
                />
              </View>
            ))}

            <TouchableOpacity style={styles.importButton} onPress={onMapAndImport}>
              <Text style={styles.importButtonText}>Map & Import</Text>
            </TouchableOpacity>
          </View>
        )}

        {preview.length > 0 && (
          <View style={styles.preview}>
            <Text style={styles.subtitle}>Preview</Text>
            <FlatList
              data={preview}
              keyExtractor={(item, idx) => String(idx)}
              renderItem={({ item }) => (
                <View style={styles.previewRow}>
                  <Text>{JSON.stringify(item)}</Text>
                </View>
              )}
            />
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  content: { padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 12 },
  subtitle: { fontSize: 16, fontWeight: '600', marginTop: 12 },
  pasteBox: { height: 150, borderWidth: 1, borderColor: '#E5E7EB', padding: 8, marginVertical: 8 },
  mapping: { marginTop: 12 },
  mapRow: { marginBottom: 8 },
  mapLabel: { fontSize: 14, marginBottom: 4 },
  mapInput: { height: 44, borderWidth: 1, borderColor: '#E5E7EB', padding: 8, borderRadius: 6 },
  importButton: { backgroundColor: '#2563EB', padding: 12, marginTop: 12, borderRadius: 8, alignItems: 'center' },
  importButtonText: { color: '#fff', fontWeight: '600' },
  preview: { marginTop: 16 },
  previewRow: { padding: 8, borderBottomWidth: 1, borderBottomColor: '#F3F4F6' }
});
