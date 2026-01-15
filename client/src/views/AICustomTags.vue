<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">
      🎨 AI Custom Tags Manager
    </div>

    <q-banner class="bg-info text-white q-mb-md" rounded>
      <template v-slot:avatar>
        <q-icon name="mdi-information" color="white" />
      </template>
      Define your own genre, mood, and vibe tags for AI-powered tagging.
      These tags will be used by Gemini AI to categorize your tracks.
    </q-banner>

    <!-- Genre Tags -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6">🎵 Custom Genres</div>
        <div class="text-caption text-grey-7">
          Define your personal genre taxonomy (e.g., "deep-techno", "melodic-house")
        </div>
      </q-card-section>

      <q-card-section>
        <q-chip
          v-for="(tag, index) in customTags.genres"
          :key="'genre-' + index"
          removable
          @remove="removeTag('genres', index)"
          color="primary"
          text-color="white"
        >
          {{ tag }}
        </q-chip>

        <q-input
          v-model="newGenreTag"
          dense
          placeholder="Add new genre tag..."
          @keyup.enter="addTag('genres', newGenreTag); newGenreTag = ''"
          class="q-mt-sm"
        >
          <template v-slot:append>
            <q-btn
              flat
              dense
              icon="mdi-plus"
              @click="addTag('genres', newGenreTag); newGenreTag = ''"
              :disable="!newGenreTag.trim()"
            />
          </template>
        </q-input>
      </q-card-section>
    </q-card>

    <!-- Mood Tags -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6">😊 Custom Moods</div>
        <div class="text-caption text-grey-7">
          Define mood tags for your tracks (e.g., "dark", "uplifting", "hypnotic")
        </div>
      </q-card-section>

      <q-card-section>
        <q-chip
          v-for="(tag, index) in customTags.moods"
          :key="'mood-' + index"
          removable
          @remove="removeTag('moods', index)"
          color="secondary"
          text-color="white"
        >
          {{ tag }}
        </q-chip>

        <q-input
          v-model="newMoodTag"
          dense
          placeholder="Add new mood tag..."
          @keyup.enter="addTag('moods', newMoodTag); newMoodTag = ''"
          class="q-mt-sm"
        >
          <template v-slot:append>
            <q-btn
              flat
              dense
              icon="mdi-plus"
              @click="addTag('moods', newMoodTag); newMoodTag = ''"
              :disable="!newMoodTag.trim()"
            />
          </template>
        </q-input>
      </q-card-section>
    </q-card>

    <!-- Situation Tags -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6">📍 Situation Tags</div>
        <div class="text-caption text-grey-7">
          Define situation/time tags (e.g., "Intro", "Peak", "Warmup", "After")
        </div>
      </q-card-section>

      <q-card-section>
        <q-chip
          v-for="(tag, index) in customTags.vibes"
          :key="'vibe-' + index"
          removable
          @remove="removeTag('vibes', index)"
          color="accent"
          text-color="white"
        >
          {{ tag }}
        </q-chip>

        <q-input
          v-model="newVibeTag"
          dense
          placeholder="Add new vibe tag..."
          @keyup.enter="addTag('vibes', newVibeTag); newVibeTag = ''"
          class="q-mt-sm"
        >
          <template v-slot:append>
            <q-btn
              flat
              dense
              icon="mdi-plus"
              @click="addTag('vibes', newVibeTag); newVibeTag = ''"
              :disable="!newVibeTag.trim()"
            />
          </template>
        </q-input>
      </q-card-section>
    </q-card>

    <!-- Preset Templates -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6">📋 Quick Presets</div>
        <div class="text-caption text-grey-7 q-mb-md">
          Load pre-defined tag collections for common DJ genres
        </div>

        <q-btn-group>
          <q-btn
            label="Techno"
            icon="mdi-lightning-bolt"
            @click="loadPreset('techno')"
            outline
            color="primary"
          />
          <q-btn
            label="House"
            icon="mdi-home"
            @click="loadPreset('house')"
            outline
            color="primary"
          />
          <q-btn
            label="Trance"
            icon="mdi-airplane-takeoff"
            @click="loadPreset('trance')"
            outline
            color="primary"
          />
          <q-btn
            label="Hip-Hop"
            icon="mdi-microphone"
            @click="loadPreset('hiphop')"
            outline
            color="primary"
          />
        </q-btn-group>
      </q-card-section>
    </q-card>

    <!-- Actions -->
    <div class="row q-gutter-sm">
      <q-btn
        label="Save Tags"
        icon="mdi-content-save"
        color="primary"
        @click="saveTags"
        :loading="saving"
      />
      <q-btn
        label="Reset to Defaults"
        icon="mdi-refresh"
        color="negative"
        outline
        @click="confirmReset"
      />
      <q-btn
        label="Export"
        icon="mdi-download"
        color="grey-7"
        outline
        @click="exportTags"
      />
      <q-btn
        label="Import"
        icon="mdi-upload"
        color="grey-7"
        outline
        @click="importTags"
      />
    </div>

    <!-- Stats -->
    <q-card class="q-mt-md">
      <q-card-section>
        <div class="text-subtitle2">Tag Statistics</div>
        <div class="row q-gutter-md">
          <div>
            <div class="text-h6 text-primary">{{ customTags.genres.length }}</div>
            <div class="text-caption">Genres</div>
          </div>
          <div>
            <div class="text-h6 text-secondary">{{ customTags.moods.length }}</div>
            <div class="text-caption">Moods</div>
          </div>
          <div>
            <div class="text-h6 text-accent">{{ customTags.vibes.length }}</div>
            <div class="text-caption">Situations</div>
          </div>
          <div>
            <div class="text-h6 text-positive">{{ totalTags }}</div>
            <div class="text-caption">Total Tags</div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';

export default {
  name: 'AICustomTags',

  setup() {
    const $q = useQuasar();

    // State
    const customTags = ref({
      genres: [
        'Ambient',
        'Acid',
        'Breaks',
        'Deep',
        'Dub',
        'Electro',
        'House',
        'Minimal',
        'Techno',
        'Techouse',
      ],
      moods: [
        'Dark',
        'Cosmic',
        'Beautiful',
        'Nasty',
        'Trippy',
        'Battle',
        'Upper',
        'Proper',
        'Schizo',
        'Raw',
        'Oldek',
      ],
      vibes: [
        'Intro',
        'Warmup',
        'Peak',
        'Filler',
        'After',
        'Outro',
        'Morning',
        'Daytime',
        'Tool',
      ],
    });

    const newGenreTag = ref('');
    const newMoodTag = ref('');
    const newVibeTag = ref('');
    const saving = ref(false);

    // Computed
    const totalTags = computed(() => {
      return (
        customTags.value.genres.length +
        customTags.value.moods.length +
        customTags.value.vibes.length
      );
    });

    // Methods
    const addTag = (category, tag) => {
      const cleanTag = tag.trim().toLowerCase().replace(/\s+/g, '-');
      if (cleanTag && !customTags.value[category].includes(cleanTag)) {
        customTags.value[category].push(cleanTag);
      }
    };

    const removeTag = (category, index) => {
      customTags.value[category].splice(index, 1);
    };

    const saveTags = async () => {
      saving.value = true;
      try {
        // TODO: Call backend API to save tags
        await new Promise((resolve) => setTimeout(resolve, 500));
        $q.notify({
          type: 'positive',
          message: 'Custom tags saved successfully!',
          icon: 'check_circle',
        });
      } catch (error) {
        $q.notify({
          type: 'negative',
          message: 'Failed to save tags: ' + error.message,
          icon: 'error',
        });
      } finally {
        saving.value = false;
      }
    };

    const confirmReset = () => {
      $q.dialog({
        title: 'Reset to Defaults',
        message: 'Are you sure you want to reset all custom tags to default values?',
        cancel: true,
        persistent: true,
      }).onOk(() => {
        resetToDefaults();
      });
    };

    const resetToDefaults = () => {
      customTags.value = {
        genres: ['Ambient', 'Techno', 'House', 'Minimal'],
        moods: ['Dark', 'Cosmic', 'Beautiful', 'Upper'],
        vibes: ['Intro', 'Warmup', 'Peak', 'After'],
      };
      $q.notify({
        type: 'info',
        message: 'Tags reset to defaults',
        icon: 'refresh',
      });
    };

    const loadPreset = (preset) => {
      const presets = {
        techno: {
          genres: ['Techno', 'Minimal', 'Acid', 'Electro'],
          moods: ['Dark', 'Cosmic', 'Raw', 'Schizo'],
          vibes: ['Peak', 'After', 'Morning'],
        },
        house: {
          genres: ['House', 'Techouse', 'Deep', 'Funky'],
          moods: ['Upper', 'Beautiful', 'Proper'],
          vibes: ['Warmup', 'Peak', 'Daytime'],
        },
        trance: {
          genres: ['Progressive', 'Ambient'],
          moods: ['Cosmic', 'Trippy', 'Beautiful'],
          vibes: ['Intro', 'Peak', 'Outro'],
        },
        hiphop: {
          genres: ['Breaks', 'Drum & Bass'],
          moods: ['Battle', 'Nasty', 'Upper'],
          vibes: ['Peak', 'Filler'],
        },
      };

      if (presets[preset]) {
        customTags.value = { ...presets[preset] };
        $q.notify({
          type: 'positive',
          message: `Loaded ${preset} preset`,
          icon: 'check_circle',
        });
      }
    };

    const exportTags = () => {
      const dataStr = JSON.stringify(customTags.value, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
      const exportFileDefaultName = 'custom-tags.json';

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();

      $q.notify({
        type: 'positive',
        message: 'Tags exported successfully',
        icon: 'download',
      });
    };

    const importTags = () => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.json';
      input.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const imported = JSON.parse(event.target.result);
            if (imported.genres && imported.moods && imported.vibes) {
              customTags.value = imported;
              $q.notify({
                type: 'positive',
                message: 'Tags imported successfully',
                icon: 'upload',
              });
            } else {
              throw new Error('Invalid format');
            }
          } catch (error) {
            $q.notify({
              type: 'negative',
              message: 'Failed to import tags: Invalid file format',
              icon: 'error',
            });
          }
        };
        reader.readAsText(file);
      };
      input.click();
    };

    return {
      customTags,
      newGenreTag,
      newMoodTag,
      newVibeTag,
      saving,
      totalTags,
      addTag,
      removeTag,
      saveTags,
      confirmReset,
      loadPreset,
      exportTags,
      importTags,
    };
  },
};
</script>

<style scoped>
.q-chip {
  margin: 4px;
}
</style>
