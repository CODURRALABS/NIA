import { supabase } from './supabaseClient';

export interface NiaSettings {
    id?: string;
    user_id: string;
    language: string;
    voice_id: string;
    greeting_en: string;
    greeting_hi: string;
    persona_name: string;
    relationship: string;
    wake_word: string;
}

const DEFAULT_SETTINGS: Omit<NiaSettings, 'id'> = {
    user_id: 'default_user', // Fallback for local dev without auth
    language: 'hi-IN',
    voice_id: 'meera',
    greeting_en: 'Hello! How can I help you today?',
    greeting_hi: 'नमस्कार! बॉस, मैं आज आपकी मदद कैसे कर सकता हूँ?',
    persona_name: 'NIA',
    relationship: 'Companion',
    wake_word: 'Nia'
};

export const getNiaSettings = async (userId: string = 'default_user'): Promise<NiaSettings> => {
    // 1. Try Local Storage first for immediate responsiveness and fallback
    const local = typeof window !== 'undefined' ? localStorage.getItem(`nia_settings_${userId}`) : null;
    let localData = local ? JSON.parse(local) : null;

    try {
        const { data, error } = await supabase
            .from('nia_settings')
            .select('*')
            .eq('user_id', userId)
            .single();

        if (error) {
            // PGRST205 means table doesn't exist. We handle this gracefully.
            if (error.code === 'PGRST205') {
                console.warn('Supabase: "nia_settings" table not found. Using Local Fallback Mode.');
                return localData || { ...DEFAULT_SETTINGS, user_id: userId };
            }

            if (error.code !== 'PGRST116') {
                console.error('Supabase Fetch Error:', error.message);
                return localData || { ...DEFAULT_SETTINGS, user_id: userId };
            }
        }

        if (!data) {
            // Attempt to sync local to cloud if table exists
            const { data: newData, error: createError } = await supabase
                .from('nia_settings')
                .insert([localData || { ...DEFAULT_SETTINGS, user_id: userId }])
                .select()
                .single();

            if (createError) {
                // If table creation fails (likely legacy/missing), just use local
                return localData || { ...DEFAULT_SETTINGS, user_id: userId };
            }
            return newData;
        }

        // Cache cloud data to local for offline/fast access
        if (typeof window !== 'undefined') {
            localStorage.setItem(`nia_settings_${userId}`, JSON.stringify(data));
        }

        return data;
    } catch (err) {
        return localData || { ...DEFAULT_SETTINGS, user_id: userId };
    }
};

export const updateNiaSettings = async (userId: string, updates: Partial<NiaSettings>) => {
    // 1. Prepare merged data
    let currentData = DEFAULT_SETTINGS;
    if (typeof window !== 'undefined') {
        const current = localStorage.getItem(`nia_settings_${userId}`);
        if (current) currentData = JSON.parse(current);
    }
    const merged = { ...currentData, ...updates, user_id: userId };

    // 2. Update Local Storage First
    if (typeof window !== 'undefined') {
        localStorage.setItem(`nia_settings_${userId}`, JSON.stringify(merged));
    }

    // 3. Try to sync to Supabase
    try {
        const { data, error } = await supabase
            .from('nia_settings')
            .upsert(merged)
            .select()
            .single();

        if (error) {
            if (error.code !== 'PGRST205') {
                console.error('Supabase Sync Error:', error.message);
            }
            // Return merged local data on sync failure so UI stays in sync
            return merged as NiaSettings;
        }
        return data;
    } catch (err: any) {
        if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
            // Silently transition to Sovereign Offline mode
            return merged as NiaSettings;
        }
        console.warn('Cloud sync failed, settings saved locally.');
        return merged as NiaSettings;
    }
};
