import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function Survey() {
  return (
    <View style={styles.container}>
      <Text>Survey Screen</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
