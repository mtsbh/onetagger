<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">
      🎨 AI Custom Tags Manager
    </div>

    <q-banner class="bg-info text-white q-mb-md" rounded>
      <template v-slot:avatar>
        <q-icon name="info" color="white" />
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
          icon="music_note"
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
              icon="add"
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
          icon="mood"
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
              icon="add"
              @click="addTag('moods', newMoodTag); newMoodTag = ''"
              :disable="!newMoodTag.trim()"
            />
          </template>
        </q-input>
      </q-card-section>
    </q-card>

    <!-- Vibe Tags -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6">✨ Custom Vibes</div>
        <div class="text-caption text-grey-7">
          Define vibe/context tags (e.g., "warehouse", "beach-sunset", "peak-time")
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
          icon="wb_twilight"
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
              icon="add"
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
            icon="flash_on"
            @click="loadPreset('techno')"
            outline
            color="primary"
          />
          <q-btn
            label="House"
            icon="home"
            @click="loadPreset('house')"
            outline
            color="primary"
          />
          <q-btn
            label="Trance"
            icon="flight_takeoff"
            @click="loadPreset('trance')"
            outline
            color="primary"
          />
          <q-btn
            label="Hip-Hop"
            icon="mic"
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
        icon="save"
        color="primary"
        @click="saveTags"
        :loading="saving"
      />
      <q-btn
        label="Reset to Defaults"
        icon="refresh"
        color="negative"
        outline
        @click="confirmReset"
      />
      <q-btn
        label="Export"
        icon="download"
        color="grey-7"
        outline
        @click="exportTags"
      />
      <q-btn
        label="Import"
        icon="upload"
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
            <div class="text-caption">Vibes</div>
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
        'deep-techno',
        'melodic-techno',
        'peak-time-techno',
        'minimal-techno',
        'progressive-house',
        'deep-house',
        'tech-house',
        'melodic-house',
      ],
      moods: [
        'dark',
        'uplifting',
        'melancholic',
        'euphoric',
        'hypnotic',
        'groovy',
      ],
      vibes: [
        'warehouse',
        'beach-sunset',
        'peak-time',
        'warm-up',
        'after-hours',
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
        genres: ['deep-techno', 'melodic-techno', 'peak-time-techno'],
        moods: ['dark', 'uplifting', 'hypnotic'],
        vibes: ['warehouse', 'beach-sunset', 'peak-time'],
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
          genres: ['deep-techno', 'melodic-techno', 'peak-time-techno', 'minimal-techno', 'industrial-techno'],
          moods: ['dark', 'hypnotic', 'driving', 'intense'],
          vibes: ['warehouse', 'underground', 'peak-time', 'after-hours'],
        },
        house: {
          genres: ['deep-house', 'tech-house', 'progressive-house', 'melodic-house', 'jackin-house'],
          moods: ['groovy', 'uplifting', 'soulful', 'funky'],
          vibes: ['beach-club', 'rooftop', 'sunset', 'poolside'],
        },
        trance: {
          genres: ['progressive-trance', 'uplifting-trance', 'psy-trance', 'tech-trance'],
          moods: ['euphoric', 'uplifting', 'emotional', 'energetic'],
          vibes: ['festival', 'mainstage', 'journey', 'peak-time'],
        },
        hiphop: {
          genres: ['trap', 'boom-bap', 'conscious-rap', 'drill', 'cloud-rap'],
          moods: ['chill', 'aggressive', 'smooth', 'energetic'],
          vibes: ['club', 'car-music', 'workout', 'late-night'],
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
