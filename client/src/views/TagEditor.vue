<template>
<div class='full-height'>

    <div class='row full-height'>
        <!-- File browser -->
        <div
            @contextmenu.prevent=""
            class='q-px-md q-pt-md bg-darker'
            :class='{"col-4": !$1t.settings.value.tagEditorDouble, "col-3": $1t.settings.value.tagEditorDouble}'
            style='max-height: 100%; overflow-y: scroll;'
        >
            <div class='row items-center justify-between q-mb-sm'>
                <div class='text-weight-bold text-subtitle2 clickable path-display' @click='browse' style="flex: 1;">
                    <div class='row inline'>
                        <span style="direction:ltr;" class='text-primary monospace'>{{path}}</span>
                    </div>
                </div>
            </div>

            <!-- Bulk Mode Toggle (Always Visible) -->
            <div class="q-mb-sm">
                <q-btn-toggle
                    v-model="bulkMode"
                    spread
                    dense
                    no-caps
                    toggle-color="primary"
                    color="dark"
                    text-color="grey-4"
                    :options="[
                        {label: 'Single Edit', value: false},
                        {label: 'Bulk Operations', value: true}
                    ]"
                    @update:model-value="onModeChange"
                />
            </div>

            <div class='q-mt-sm'>

                <!-- Filter -->
                <q-input dense filled label='Filter' class='q-mb-sm' @update:model-value='(v: any) => applyFilter(v as string)' v-model='filter'></q-input>

                <!-- Bulk mode controls -->
                <div v-if="bulkMode" class="q-mb-sm bg-dark q-pa-sm rounded-borders">
                    <div class="row q-mb-xs q-gutter-xs items-center">
                        <q-btn dense size="xs" push label="Select All" @click="selectAllFiles" color="primary" icon="mdi-checkbox-multiple-marked" />
                        <q-btn dense size="xs" push label="Clear" @click="clearSelection" color="grey-7" icon="mdi-close" />
                    </div>
                    <div class="text-caption text-grey-4 text-center">
                        <strong class="text-primary">{{ selectedFilesCount }}</strong> files selected
                    </div>
                </div>

                <!-- Parent -->
                <div class='q-mb-sm clickable te-file' @click='loadFiles("..")'>
                    <q-icon size='xs' class='q-mb-xs text-grey-4' name='mdi-folder-upload'></q-icon>
                    <span class='q-ml-sm text-caption text-grey-4'>Parent folder</span>
                </div>

                <draggable
                    id='fileList'
                    :move='onFileMove'
                    group='files'
                    :list='files'
                    item-key='filename'
                    @change='onFileDrag'>
                    <template #item='{ element: file }'>
                        <div
                            class='clickable te-file row items-center no-wrap'
                            @click='handleFileClick(file)'
                            @dblclick='bulkMode && !file.dir ? playFile(file.path) : null'
                            :class='{"text-primary": (!bulkMode && isSelected(file.path)) || (bulkMode && isFileSelected(file.path)), "text-grey-4": (!bulkMode && !isSelected(file.path)) && !(bulkMode && isFileSelected(file.path))}'
                        >
                            <!-- Checkbox for files in bulk mode -->
                            <q-checkbox
                                v-if="bulkMode && !file.dir && !file.playlist"
                                dense
                                :model-value="isFileSelected(file.path)"
                                @update:model-value="toggleFileSelection(file.path)"
                                @click.stop
                                size="xs"
                                class="q-mr-xs"
                            />
                            <!-- Button for folders in bulk mode to select all files in folder -->
                            <q-btn
                                v-if="bulkMode && file.dir"
                                dense
                                flat
                                round
                                size="xs"
                                icon="mdi-checkbox-marked-circle-plus-outline"
                                @click.stop="selectFolder(file.filename)"
                                color="primary"
                                class="q-mr-xs"
                            >
                                <q-tooltip>Select all files in this folder</q-tooltip>
                            </q-btn>
                            <q-icon size='xs' class='q-mb-xs text-grey-4' v-if='!file.dir && !file.playlist' name='mdi-music'></q-icon>
                            <q-icon size='xs' class='q-mb-xs text-grey-4' v-if='file.dir' name='mdi-folder'></q-icon>
                            <q-icon size='xs' class='q-mb-xs text-grey-4' v-if='file.playlist' name='mdi-playlist-music'></q-icon>
                            <span class='q-ml-sm text-caption'>{{file.filename}}</span>
                        </div>
                    </template>

                    
                </draggable>
            </div>
        </div>

        <!-- Custom list -->
        <div 
            @contextmenu.prevent="" 
            class='col-3 bg-darker q-px-md q-pt-sm' 
            v-if='$1t.settings.value.tagEditorDouble'
            style='max-height: 100%; overflow-y: scroll;'
        >
            <div class='bg-darker separator'></div>
            <div class='row justify-between'>
                <div class='text-weight-bold text-subtitle2 text-primary q-pb-sm'>Your list</div>
                <div>
                    <q-btn round dense size='xs' flat style='margin-right: 2px;' @click='clearCustom'>
                        <q-icon name='mdi-close' color='red'></q-icon>
                    </q-btn>
                </div>
            </div>
            
            <draggable 
                group='files' 
                :move='onFileMove' 
                :list='customList' 
                @change='onFileDrag' 
                style='height: calc(100% - 32px)'
                :item-key="(e: any) => `//CUSTOM${e}`"
            >
                <template #item='{ element: f }'>
                    <div class='row'>
                        <div 
                            @click='loadFile(f)' 
                            class='te-file clickable q-my-xs q-mr-sm' 
                            style='width: calc(100% - 32px)' 
                            :class='{"text-primary": isSelected(f), "text-grey-4": !isSelected(f)}'
                        >
                            <span>{{filename(f)}}</span>
                        </div>
                        <div>
                            <q-btn size='xs' class='q-mt-xs' flat round style='float: right;' @click='removeCustom(f)'>
                                <q-icon name='mdi-close' color='red'></q-icon>
                            </q-btn>
                        </div>
                    </div>
                </template>
            </draggable>
        </div>

        <!-- Tags (Single Edit Mode) -->
        <div
            v-if="!bulkMode"
            :class='{"col-8": !$1t.settings.value.tagEditorDouble, "col-6": $1t.settings.value.tagEditorDouble}'
            style='max-height: 100%; overflow-y: scroll;'>
            <div v-if='!file' class='justify-center items-center content-center row full-height'>

                <div class='col-12 text-subtitle2 text-bold text-primary text-center q-my-sm'>NO FILE SELECTED</div><br>
                <span class='text-center text-subtitle2 text-grey-6'>Tip: <span class='keybind-icon q-px-sm text-caption text-bold'>CLICK</span> the path to open a folder and select an audio file</span>
            </div>

            <div v-if='file' class='q-px-md'>
                <div class='text-center q-py-md text-subtitle2 text-grey-5 monospace'>{{file.filename}}</div>
                <div class='q-mt-md'>
                    <div v-for='(tag, i) in Object.keys(file.tags)' :key='i' class='row q-my-sm'>
                        <div class='col-3 text-body2 text-uppercase text-primary text-weight-medium q-mt-sm q-pr-xs' style='text-overflow: ellipsis; overflow: hidden;'>
                            
                            <span v-if='ABSTRACTIONS[tag]'><span class='text-uppercase text-primary text-weight-medium'>{{ABSTRACTIONS[tag]}} </span><span class="text-grey-4 monospace text-caption"> {{tag}}</span></span>
                            <span v-if='!ABSTRACTIONS[tag]'>{{tag}}</span>
                        </div>
                        
                        
                        <q-input
                            v-model='file.tags[tag]'
                            filled
                            dense
                            class='col-8'
                            @change='onChange(tag)'
                        ></q-input>

                        <div class='col-1 q-pl-md q-pt-xs'>
                            <q-btn round dense flat @click='removeTag(tag)'>
                                <q-icon name='mdi-delete' class='text-red'></q-icon>
                            </q-btn>
                        </div>
                    </div>
                </div>
                <q-separator class='q-mx-auto' :style='"max-width: 513px; margin-top: 40px;"' inset color="dark"/>
                
                <!-- Add new tag -->
                <div class='row q-mt-lg' style='margin-top: 40px;'>
                    <div class='col-3 q-pt-sm text-weight-medium text-grey-4 text-body2'>Add new text tag</div>
                    <TagField tageditor class='col-8' dense :format='tagFormat!' @update:model-value='newTag = $event'></TagField>
                    <div class='col-1 q-pl-md q-pt-xs'>
                        <q-btn round dense flat @click='addNewTag'>
                            <q-icon name='mdi-plus' class='text-primary'></q-icon>
                        </q-btn>
                    </div>
                </div>
                <q-separator class='q-mx-auto' :style='"max-width: 513px; margin-top: 20px; margin-bottom: 25px;"' inset color="dark"/>
                
                <!-- Album art -->
                <div class='text-uppercase text-primary text-weight-medium'>
                    Album art
                    <q-btn round flat class='q-mb-xs q-ml-sm' @click='addAlbumArtDialog = true'>
                        <q-icon name='mdi-plus' color='primary'></q-icon>
                    </q-btn>
                </div>
                <div class='text-grey-4 albumart-container text-center'>
                    <div v-for='(image, i) in file.images' :key='"art"+i' class='q-mr-md'>
                        <!-- <q-img :src='image.data' class='albumart clickable' @click='albumArt = image.data; showAlbumArt = true'></q-img>
                        <div class='q-pt-sm q-mb-md'>
                            <div v-if='file.format != "mp4"' class='text-caption'>{{image.kind}}</div>
                            <div v-if='file.format != "mp4"' class='text-caption'>{{image.description}}</div>
                            <div class='text-subtitle3 text-grey-6 monospace'>{{image.mime}} {{image.width}}x{{image.height}}</div>
                            <q-btn dense push color='red' class='rounded-borders q-px-md q-mt-sm text-weight-medium' @click='removeArt(i)'>Remove</q-btn>
                        </div> -->
                        <TagEditorAlbumArt 
                            :image='image' 
                            @click='albumArt = image.data; showAlbumArt = true' 
                            @remove='removeArt(i)'
                            @replace='addAlbumArt'
                        ></TagEditorAlbumArt>
                    </div>
                </div>

                <!-- ID3 specific tags -->
                <div v-if='file.id3'>
                    <!-- Comments -->
                    <div class='text-uppercase text-primary text-weight-medium'>
                        Comments <span class="text-grey-4 monospace text-caption q-pl-xs">COMM</span>
                        <q-btn round flat class='q-mb-xs q-ml-sm' @click='addID3Comment'>
                            <q-icon name='mdi-plus' color='primary'></q-icon>
                        </q-btn>
                    </div>
                    <div>
                        <div v-for='(comment, i) in file.id3.comments' :key='"comm"+i' class='row q-py-sm'>
                            <q-input
                                filled
                                dense
                                label='Language'
                                class='col-2'
                                v-model='file.id3.comments[i].lang'
                                maxlength='3'
                                @change='id3CommentsChange'
                            ></q-input>
                            <q-input
                                filled
                                dense
                                label='Description'
                                class='col-4 q-pl-sm'
                                v-model='file.id3.comments[i].description'
                                @change='id3CommentsChange'
                            ></q-input>
                            <q-input
                                filled
                                dense
                                label='Text'
                                class='col-5 q-pl-sm'
                                v-model='file.id3.comments[i].text'
                                @change='id3CommentsChange'
                            ></q-input>
                            <div class='col-1 q-pl-md q-pt-xs'>
                                <q-btn round dense flat @click='removeID3Comment(i)'>
                                    <q-icon name='mdi-delete' class='text-red'></q-icon>
                                </q-btn>
                            </div>
                        </div>
                    </div>

                    <!-- Unsynchronized lyrics -->
                    <div class='text-uppercase text-primary text-weight-medium'>
                        Unsynchronized lyrics <span class="text-grey-4 monospace text-caption q-pl-xs">USLT</span>
                        <q-btn round flat class='q-mb-xs q-ml-sm' @click='addID3USLT'>
                            <q-icon name='mdi-plus' color='primary'></q-icon>
                        </q-btn>
                    </div>
                    <div>
                        <div v-for='(lyric, i) in file.id3.unsync_lyrics' :key='"uslt"+i' class='q-py-sm'>
                            <div class='row'>
                                <q-input
                                    filled
                                    dense
                                    label='Language'
                                    class='col-3'
                                    v-model='file.id3.unsync_lyrics[i].lang'
                                    maxlength='3'
                                    @change='id3USLTChange'
                                ></q-input>
                                <q-input
                                    filled
                                    dense
                                    label='Description'
                                    class='col-8 q-pl-md'
                                    v-model='file.id3.unsync_lyrics[i].description'
                                    @change='id3USLTChange'
                                ></q-input>
                                <div class='col-1 q-pl-md q-pt-xs'>
                                    <q-btn round dense flat @click='removeID3USLT(i)'>
                                        <q-icon name='mdi-delete' class='text-red'></q-icon>
                                    </q-btn>
                                </div>
                            </div>
                            <q-input
                                filled
                                dense
                                label='Text'
                                v-model='file.id3.unsync_lyrics[i].text'
                                type='textarea'
                                class='q-pt-sm q-pb-sm'
                                @change='id3USLTChange'
                            ></q-input>
                        </div>
                    </div>

                    <!-- Popularimeter -->
                    <div>
                        <div class='text-uppercase text-primary text-weight-medium'>
                            Popularimeter <span class="text-grey-4 monospace text-caption q-pl-xs">POPM</span>
                            <q-btn v-if='!file.id3.popularimeter' round flat class='q-mb-xs q-ml-sm' @click='addPOPM'>
                                <q-icon name='mdi-plus' color='primary'></q-icon>
                            </q-btn>
                        </div>
                        <div v-if='file.id3.popularimeter' class='row q-py-sm'>
                            <q-input
                                filled
                                dense
                                label='Email'
                                class='col-4'
                                v-model='file.id3.popularimeter.email'
                                @change='id3POPMChange'
                            ></q-input>
                            <q-input
                                filled
                                dense
                                type='number'
                                label='Play count'
                                class='col-3 q-pl-sm'
                                v-model='file.id3.popularimeter.counter'
                                maxlength='9'
                                @change='id3POPMChange'
                            ></q-input>
                            <div class='col-4 q-pl-md'>
                                <q-slider
                                    :min='0'
                                    :max='255'
                                    label
                                    label-text-color='black'
                                    :label-value='POPMLabel'
                                    v-model='file.id3.popularimeter.rating'
                                    @change='id3POPMChange'
                                ></q-slider>
                            </div>
                            <div class='col-1 q-pl-md q-pt-xs'>
                                <q-btn round dense flat @click='removePOPM'>
                                    <q-icon name='mdi-delete' class='text-red'></q-icon>
                                </q-btn>
                            </div>
                        </div>
                    </div>
                    <q-separator class='q-mx-auto' :style='"max-width: 513px; margin-top: 32px; margin-bottom: 25px;"' inset color="dark"/>
                    
                    <!-- ID3v2.4 -->
                    <div class='q-mt-lg text-center'>
                        <div class='text-subtitle2 text-bold text-primary custom-margin'>
                            OPTIONS
                        </div>
                    </div>
                    <div class='column flex-center'>
                        <q-toggle label='Use ID3v2.4' left-label style='width: 160px;' class='justify-between' v-model='id3v24'></q-toggle>
                    </div>
            </div>

            <!-- Save, Manual tag -->
            <q-page-sticky position='bottom-right' :offset='[36, 18]'>
                <div class='row'>
                    <q-btn dense
                        push
                        @click='manualTagPath = file.path'
                        color="primary"
                        class='rounded-borders q-px-md q-mt-xs text-black text-weight-medium q-mr-md'
                        label="Manual Tag"
                    ></q-btn>

                    <q-btn dense
                        push
                        @click='save'
                        color="primary"
                        class='rounded-borders q-px-md q-mt-xs text-black text-weight-medium'
                        label="Save"
                    ></q-btn>
                </div>
            </q-page-sticky>

            </div>
        </div>

        <!-- Bulk Operations Panel -->
        <div
            v-if="bulkMode"
            :class='{"col-8": !$1t.settings.value.tagEditorDouble, "col-6": $1t.settings.value.tagEditorDouble}'
            class="q-px-md q-pt-md"
            style='max-height: 100%; overflow-y: scroll;'>

            <!-- No files selected message -->
            <div v-if="selectedFilesCount === 0" class='justify-center items-center content-center row full-height'>
                <div>
                    <div class='col-12 text-subtitle2 text-bold text-primary text-center q-my-sm'>NO FILES SELECTED</div>
                    <span class='text-center text-subtitle2 text-grey-6'>Select audio files from the left panel to apply bulk operations</span>
                </div>
            </div>

            <!-- Bulk operations -->
            <div v-if="selectedFilesCount > 0">
                <div class='text-center q-py-md text-subtitle2 text-primary'>
                    Bulk Operations ({{ selectedFilesCount }} files selected)
                </div>

                <!-- Replace Text Operation -->
                <q-expansion-item
                    v-model="bulkOperations.replace.enabled"
                    icon="mdi-find-replace"
                    label="Replace Text"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm">
                    <q-card class="bg-darker q-pa-md">
                        <div class="q-gutter-sm">
                            <q-select
                                dense
                                filled
                                v-model="bulkOperations.replace.field"
                                :options="fieldOptions"
                                label="Field"
                            />
                            <q-input
                                dense
                                filled
                                v-model="bulkOperations.replace.find"
                                label="Find"
                                placeholder="Text to find"
                            />
                            <q-input
                                dense
                                filled
                                v-model="bulkOperations.replace.replaceWith"
                                label="Replace with"
                                placeholder="Replacement text"
                            />
                            <div class="row q-gutter-sm">
                                <q-checkbox v-model="bulkOperations.replace.caseSensitive" label="Case sensitive" dense />
                                <q-checkbox v-model="bulkOperations.replace.useRegex" label="Use regex" dense />
                            </div>
                        </div>
                    </q-card>
                </q-expansion-item>

                <!-- Trim Whitespace Operation -->
                <q-expansion-item
                    v-model="bulkOperations.trim.enabled"
                    icon="mdi-format-text"
                    label="Trim Whitespace"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm">
                    <q-card class="bg-darker q-pa-md">
                        <div class="q-gutter-sm">
                            <q-select
                                dense
                                filled
                                v-model="bulkOperations.trim.field"
                                :options="['ALL FIELDS', ...fieldOptions]"
                                label="Field"
                            />
                            <div class="row q-gutter-sm">
                                <q-checkbox v-model="bulkOperations.trim.leading" label="Leading" dense />
                                <q-checkbox v-model="bulkOperations.trim.trailing" label="Trailing" dense />
                            </div>
                        </div>
                    </q-card>
                </q-expansion-item>

                <!-- Copy Field Operation -->
                <q-expansion-item
                    v-model="bulkOperations.copyField.enabled"
                    icon="mdi-content-copy"
                    label="Copy Field"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm">
                    <q-card class="bg-darker q-pa-md">
                        <div class="q-gutter-sm">
                            <q-select
                                dense
                                filled
                                v-model="bulkOperations.copyField.from"
                                :options="fieldOptions"
                                label="From"
                            />
                            <q-select
                                dense
                                filled
                                v-model="bulkOperations.copyField.to"
                                :options="fieldOptions"
                                label="To"
                            />
                            <q-checkbox v-model="bulkOperations.copyField.append" label="Append (not replace)" dense />
                        </div>
                    </q-card>
                </q-expansion-item>

                <!-- Change Case Operation -->
                <q-expansion-item
                    v-model="bulkOperations.changeCase.enabled"
                    icon="mdi-format-letter-case"
                    label="Change Case"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm">
                    <q-card class="bg-darker q-pa-md">
                        <div class="q-gutter-sm">
                            <q-select
                                dense
                                filled
                                v-model="bulkOperations.changeCase.field"
                                :options="['ALL FIELDS', ...fieldOptions]"
                                label="Field"
                            />
                            <q-select
                                dense
                                filled
                                v-model="bulkOperations.changeCase.case"
                                :options="['Title Case', 'UPPERCASE', 'lowercase']"
                                label="Case"
                            />
                        </div>
                    </q-card>
                </q-expansion-item>

                <!-- Preview and Apply buttons -->
                <div class="row justify-end q-mt-lg q-gutter-sm">
                    <q-btn
                        dense
                        push
                        color="grey-7"
                        class="rounded-borders q-px-md text-weight-medium"
                        label="Preview"
                        icon="mdi-eye"
                        @click="previewBulkOperations"
                        :disable="!hasEnabledBulkOperations"
                    />
                    <q-btn
                        dense
                        push
                        color="primary"
                        class="rounded-borders q-px-md text-weight-medium text-black"
                        label="Apply"
                        icon="mdi-check"
                        @click="applyBulkOperations"
                        :disable="!hasEnabledBulkOperations"
                    />
                </div>

                <!-- Preview Text -->
                <div v-if="bulkPreview" class="q-mt-lg q-pa-md bg-dark rounded-borders">
                    <div class="text-subtitle2 text-primary q-mb-sm">Preview:</div>
                    <div class="text-caption text-grey-4 monospace" style="white-space: pre-wrap;">{{ bulkPreview }}</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Album art dialog -->
    <q-dialog v-model='showAlbumArt' @hide='albumArt = null'>
        <q-img :src='albumArt' style='max-width: 50%;'></q-img>
    </q-dialog>

    <!-- Add album art dialog -->
    <q-dialog v-model='addAlbumArtDialog'>
        <AddAlbumArt :types='albumArtTypes' @close='addAlbumArtDialog = false' @save='addAlbumArt'></AddAlbumArt>
    </q-dialog>

    <!-- Manual Tag -->
    <ManualTag :path='manualTagPath' @exit='loadFile(manualTagPath!); manualTagPath = undefined;'></ManualTag>

</div>
</template>

<script lang='ts' setup>
import TagField from '../components/TagField.vue';
import AddAlbumArt from '../components/AddAlbumArt.vue';
import draggable from 'vuedraggable';
import { ABSTRACTIONS } from '../scripts/tags';
import { computed, onDeactivated, onMounted, ref } from 'vue';
import { get1t } from '../scripts/onetagger';
import { useQuasar } from 'quasar';
import ManualTag from '../components/ManualTag.vue';
import TagEditorAlbumArt from '../components/TagEditorAlbumArt.vue';

const $1t = get1t();
const $q = useQuasar();
const path = ref($1t.settings.value.path);
const files = ref<any[]>([]);
const originalFiles = ref<any[]>([]);
const file = ref<any>(undefined);
const filter = ref<any>(undefined);
const changes = ref<any[]>([]);
const newTag = ref<any>(undefined);
const albumArt = ref<any>(undefined);
const showAlbumArt = ref(false);
const addAlbumArtDialog = ref(false);
const customList = ref($1t.settings.value.tagEditorCustom);
const id3v24 = ref(false);
const manualTagPath = ref<string | undefined>(undefined);

// Bulk mode state
const bulkMode = ref(false);
const selectedFiles = ref<Set<string>>(new Set());
const bulkPreview = ref('');

// Bulk operations state
const bulkOperations = ref({
    replace: {
        enabled: false,
        field: 'title',
        find: '',
        replaceWith: '',
        caseSensitive: false,
        useRegex: false
    },
    trim: {
        enabled: false,
        field: 'ALL FIELDS',
        leading: true,
        trailing: true
    },
    copyField: {
        enabled: false,
        from: 'artist',
        to: 'album_artist',
        append: false
    },
    changeCase: {
        enabled: false,
        field: 'title',
        case: 'Title Case'
    }
});

const fieldOptions = [
    'title',
    'artist',
    'album',
    'album_artist',
    'genre',
    'date',
    'year',
    'comment',
    'track',
    'disc'
];

// Computed properties for bulk mode
const selectedFilesCount = computed(() => selectedFiles.value.size);
const hasEnabledBulkOperations = computed(() =>
    Object.values(bulkOperations.value).some((op: any) => op.enabled)
);


function loadFiles(f?: string) {
    $1t.send('tagEditorFolder', {path: path.value, subdir: f});
}

function browse() {
    $1t.browse('te', path.value);
}

function loadFile(path: string) {
    // Autosave
    if (file.value && $1t.settings.value.tagEditorAutosave) {
        save();
    }
    changes.value = [];

    // Will be joined in backend
    $1t.send('tagEditorLoad', {path});
    if ($1t.settings.value.tagEditorPlayer)
        $1t.player.value.loadTrack(path);
}

// If file is currently open
function isSelected(path: string) {
    if (!file.value) return false;
    return file.value.path == path;
}

function applyFilter(v: string) {
    filter.value = v;
    if (!filter.value || filter.value.trim().length == 0) {
        files.value = originalFiles.value;
        return;
    }
    files.value = originalFiles.value.filter(f => f.filename.toLowerCase().includes(filter.value));
}

/*
    Bulk Mode Functions
*/

function toggleBulkMode() {
    bulkMode.value = !bulkMode.value;
    if (!bulkMode.value) {
        selectedFiles.value.clear();
        bulkPreview.value = '';
    }
}

function onModeChange(newMode: boolean) {
    if (!newMode) {
        selectedFiles.value.clear();
        bulkPreview.value = '';
    }
}

function handleFileClick(fileItem: any) {
    if (fileItem.dir || fileItem.playlist) {
        if (!bulkMode.value) {
            loadFiles(fileItem.filename);
        }
    } else if (bulkMode.value) {
        toggleFileSelection(fileItem.path);
    } else {
        loadFile(fileItem.path);
    }
}

async function selectFolder(folderName: string) {
    // Request backend to load all files from the folder recursively
    const currentPath = path.value;
    const folderPath = currentPath + '/' + folderName;

    $q.notify({
        message: `Loading files from ${folderName}...`,
        color: 'info',
        position: 'top-right',
        timeout: 1000
    });

    // Send request to load folder recursively
    $1t.send('tagEditorFolder', {
        path: currentPath,
        subdir: folderName,
        recursive: true
    });

    // The response will come through onTagEditorEvent and populate files.value
    // Then we'll auto-select all audio files
    // Give it a moment to load
    setTimeout(() => {
        selectAllFiles();
    }, 500);
}

function isFileSelected(path: string) {
    return selectedFiles.value.has(path);
}

function toggleFileSelection(path: string) {
    if (selectedFiles.value.has(path)) {
        selectedFiles.value.delete(path);
    } else {
        selectedFiles.value.add(path);
    }
}

function selectAllFiles() {
    files.value.forEach(f => {
        if (!f.dir && !f.playlist) {
            selectedFiles.value.add(f.path);
        }
    });
}

function clearSelection() {
    selectedFiles.value.clear();
}

function playFile(filePath: string) {
    // Play the file in the player
    $1t.player.value.loadTrack(filePath);
    $1t.player.value.play();
}

function applyOperationToTag(value: string, ops: any): string {
    let result = value;

    // Replace
    if (ops.replace.enabled) {
        if (ops.replace.useRegex) {
            const flags = ops.replace.caseSensitive ? 'g' : 'gi';
            const regex = new RegExp(ops.replace.find, flags);
            result = result.replace(regex, ops.replace.replaceWith);
        } else {
            const searchValue = ops.replace.caseSensitive ? ops.replace.find : ops.replace.find.toLowerCase();
            const checkValue = ops.replace.caseSensitive ? result : result.toLowerCase();
            if (checkValue.includes(searchValue)) {
                const regex = new RegExp(ops.replace.find.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), ops.replace.caseSensitive ? 'g' : 'gi');
                result = result.replace(regex, ops.replace.replaceWith);
            }
        }
    }

    // Trim
    if (ops.trim.enabled) {
        if (ops.trim.leading && ops.trim.trailing) {
            result = result.trim();
        } else if (ops.trim.leading) {
            result = result.replace(/^\s+/, '');
        } else if (ops.trim.trailing) {
            result = result.replace(/\s+$/, '');
        }
    }

    // Change case
    if (ops.changeCase.enabled) {
        if (ops.changeCase.case === 'Title Case') {
            result = result.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
        } else if (ops.changeCase.case === 'UPPERCASE') {
            result = result.toUpperCase();
        } else if (ops.changeCase.case === 'lowercase') {
            result = result.toLowerCase();
        }
    }

    return result;
}

function previewBulkOperations() {
    let preview = 'Changes preview:\n\n';
    let fileCount = 0;
    const maxPreviewFiles = 5;

    for (const filePath of Array.from(selectedFiles.value).slice(0, maxPreviewFiles)) {
        const fileItem = files.value.find(f => f.path === filePath);
        if (!fileItem) continue;

        preview += `File: ${fileItem.filename}\n`;
        fileCount++;

        // Get current tags (this would need actual tag loading)
        preview += '  Preview not yet implemented - tags will be modified when applying\n';
        preview += '\n';
    }

    if (selectedFiles.value.size > maxPreviewFiles) {
        preview += `... and ${selectedFiles.value.size - maxPreviewFiles} more files\n`;
    }

    bulkPreview.value = preview;
}

async function applyBulkOperations() {
    const confirmed = await new Promise<boolean>(resolve => {
        $q.dialog({
            title: 'Confirm Bulk Operation',
            message: `Apply operations to ${selectedFilesCount.value} files?`,
            cancel: true,
            persistent: true
        }).onOk(() => resolve(true))
          .onCancel(() => resolve(false));
    });

    if (!confirmed) return;

    const selectedPaths = Array.from(selectedFiles.value);
    let successCount = 0;
    let errorCount = 0;

    // Show progress
    const progressNotif = $q.notify({
        group: false,
        timeout: 0,
        spinner: true,
        message: `Processing 0/${selectedPaths.length} files...`,
        position: 'top-right'
    });

    // Process each file
    for (let i = 0; i < selectedPaths.length; i++) {
        const filePath = selectedPaths[i];
        try {
            // Load the file's tags (we'll need to wait for the response)
            await loadAndProcessFile(filePath);
            successCount++;
        } catch (e) {
            console.error(`Failed to process ${filePath}:`, e);
            errorCount++;
        }

        // Update progress
        progressNotif({
            message: `Processing ${i + 1}/${selectedPaths.length} files...`
        });
    }

    // Dismiss progress
    progressNotif();

    // Show result
    $q.notify({
        message: `Bulk operations complete! ${successCount} succeeded, ${errorCount} failed.`,
        color: successCount > 0 ? 'positive' : 'negative',
        position: 'top-right',
        timeout: 3000
    });

    bulkPreview.value = '';
}

async function loadAndProcessFile(filePath: string): Promise<void> {
    return new Promise((resolve, reject) => {
        // Load file tags
        $1t.send('tagEditorLoad', {path: filePath});

        // Listen for response
        const checkLoaded = setInterval(() => {
            if (file.value && file.value.path === filePath) {
                clearInterval(checkLoaded);

                try {
                    // Apply operations to tags
                    const modifiedTags: any = {};
                    let hasChanges = false;

                    for (const [tag, value] of Object.entries(file.value.tags)) {
                        let newValue = value as string;

                        // Apply operations based on field
                        if (shouldApplyToField(tag)) {
                            const processed = applyOperationsToValue(newValue, bulkOperations.value);
                            if (processed !== newValue) {
                                modifiedTags[tag] = processed;
                                hasChanges = true;
                            }
                        }

                        // Copy field operation
                        if (bulkOperations.value.copyField.enabled) {
                            const fromField = bulkOperations.value.copyField.from.toUpperCase();
                            const toField = bulkOperations.value.copyField.to.toUpperCase();

                            if (tag.toUpperCase().includes(fromField) && file.value.tags[toField]) {
                                if (bulkOperations.value.copyField.append) {
                                    modifiedTags[toField] = file.value.tags[toField] + ' ' + value;
                                } else {
                                    modifiedTags[toField] = value;
                                }
                                hasChanges = true;
                            }
                        }
                    }

                    if (hasChanges) {
                        // Apply changes to file object
                        Object.assign(file.value.tags, modifiedTags);

                        // Save using existing save function
                        save();
                    }

                    resolve();
                } catch (e) {
                    reject(e);
                }
            }
        }, 100);

        // Timeout after 5 seconds
        setTimeout(() => {
            clearInterval(checkLoaded);
            reject(new Error('Timeout loading file'));
        }, 5000);
    });
}

function shouldApplyToField(tagName: string): boolean {
    const ops = bulkOperations.value;

    // Check if operations apply to this field
    if (ops.replace.enabled && tagName.toUpperCase().includes(ops.replace.field.toUpperCase())) {
        return true;
    }
    if (ops.trim.enabled && (ops.trim.field === 'ALL FIELDS' || tagName.toUpperCase().includes(ops.trim.field.toUpperCase()))) {
        return true;
    }
    if (ops.changeCase.enabled && (ops.changeCase.field === 'ALL FIELDS' || tagName.toUpperCase().includes(ops.changeCase.field.toUpperCase()))) {
        return true;
    }

    return false;
}

function applyOperationsToValue(value: string, ops: any): string {
    return applyOperationToTag(value, ops);
}

/*
    Custom list
*/

// Vue draggable file drag process
function onFileDrag(e: any) {
    if (e.added) {
        if (e.added.element.dir || e.added.element.playlist) {
            $1t.send('tagEditorFolder', {path: path.value, subdir: e.added.element.filename, recursive: true});
            // Don't copy
            customList.value.splice(e.added.newIndex, 1);
        } else {
            // Duplicate
            if (!customList.value.find((i) => i == e.added.element.path)) 
                customList.value.splice(e.added.newIndex, 1, e.added.element.path);
            else 
                customList.value.splice(e.added.newIndex, 1);
        }
    }
    // Read again
    if (e.removed) {
        files.value.splice(e.removed.oldIndex, 0, e.removed.element);
    }
    saveSettings();
}

// Allow only one way drag
function onFileMove(e: any) {
    if (e.relatedContext.component.$el.id == 'fileList') return false;
}
function removeCustom(i: string) {
    customList.value.splice(customList.value.indexOf(i), 1);
    saveSettings();
}

// Get filename from path
function filename(path: string) {
    path = path.toString();
    if (path.trim().startsWith('/')) {
        let s = path.split('/');
        return s[s.length - 1];
    }
    let s = path.split('\\');
    return s[s.length - 1];
}
function clearCustom() {
    customList.value = [];
    saveSettings();
}

/*
    Text Tags
*/

// Delete tag
function removeTag(tag: string) {
    delete file.value.tags[tag];
    changes.value.push({
        type: 'remove',
        tag: tag
    })
}

// Create new tag
function addNewTag() {
    if (!newTag.value) return;
    if (file.value.tags[newTag.value]) {
        $q.notify({
            message: "Tag already exists!",
            timeout: 2000,
            position: 'top-right'
        });
        return;
    }
    // Remove removal of tag
    let i = changes.value.findIndex((c) => c.type == 'remove' && c.tag == newTag.value);
    if (i > -1) changes.value.splice(i, 1);

    file.value.tags[newTag.value] = '';
    changes.value.push({
        type: 'raw',
        tag: newTag.value,
        value: []
    });
}

function onChange(tag: string) {
    let value = file.value.tags[tag]
    // Split only for tags, MP3 write to single tag as id3 separator
    if (file.value.format != 'mp3') {
        value = value.split(',');
    } else {
        value = [value];
    }
    // Generate change
    let index = changes.value.findIndex((c) => c.tag == tag);
    if (index != -1) {
        changes.value[index].value = value; 
    } else {
        changes.value.push({
            type: 'raw',
            tag: tag,
            value: value
        });
    }
}

/*
    Album Art
*/

// Add new album art
function addAlbumArt(data: any) {
    // Find old image
    file.value.images = file.value.images.filter((i: any) => i.kind != data.kind);
    changes.value = changes.value.filter((c) => c.type != 'addPictureBase64' || c.kind != data.kind);

    // Add
    changes.value.push({
        type: 'addPictureBase64',
        mime: data.mime,
        data: data.data,
        kind: data.kind,
        description: data.description
    });
    data.data = `data:${data.mime};base64,${data.data}`;
    file.value.images.push(data);
}

// Delete album art
function removeArt(i: number) {
    let kind = file.value.images[i].kind;
    file.value.images.splice(i, 1);
    //Remove newly added image
    let index = changes.value.findIndex((c) => c.type == "addPictureBase64" && c.kind == kind);
    if (index != -1) {
        changes.value.splice(index, 1);
        return;
    }
    changes.value.push({
        type: 'removePicture',
        kind
    });
}

/*
    ID3 Comments
*/

// Generate new change for ID3 comments
function id3CommentsChange() {
    let i = changes.value.findIndex((c) => c.type == 'id3Comments');
    if (i > -1) {
        changes.value.splice(i, 1);
    }
    changes.value.push({
        type: 'id3Comments',
        comments: file.value.id3.comments
    });
}

function addID3Comment() {
    file.value.id3.comments.push({
        lang: "eng",
        description: "",
        text: ""
    });
    id3CommentsChange();
}

function removeID3Comment(i: number) {
    file.value.id3.comments.splice(i, 1);
    id3CommentsChange();
}


/*
    ID3 Unsynchronized lyrics
*/
function id3USLTChange() {
    let i = changes.value.findIndex((c) => c.type == 'id3UnsynchronizedLyrics');
    if (i > -1) changes.value.splice(i, 1);
    changes.value.push({
        type: 'id3UnsynchronizedLyrics',
        lyrics: file.value.id3.unsync_lyrics
    });
}
function removeID3USLT(i: number) {
    file.value.id3.unsync_lyrics.splice(i, 1);
    id3USLTChange();
}
function addID3USLT() {
    file.value.id3.unsync_lyrics.push({
        lang: 'eng',
        description: '',
        text: ''
    });
    id3USLTChange();
}

/*
    ID3 Popularimeter
*/

function id3POPMChange() {
    // Remove existing popm changes
    let i = changes.value.findIndex((c) => c.type == 'id3Popularimeter');
    if (i > -1) changes.value.splice(i, 1);
    i = changes.value.findIndex((c) => c.type == "remove" && c.tag == "POPM");
    if (i > -1) changes.value.splice(i, 1);
    // Add new changes
    if (file.value.id3.popularimeter) {
        file.value.id3.popularimeter.counter = parseInt(file.value.id3.popularimeter.counter.toString());
        changes.value.push({
            type: 'id3Popularimeter',
            popm: file.value.id3.popularimeter
        });
    } else {
        changes.value.push({
            type: 'remove',
            tag: 'POPM'
        });
    }
}
function addPOPM() {
    file.value.id3.popularimeter = {
        email: "no@email",
        rating: 0,
        counter: 0
    }
    id3POPMChange();
}
function removePOPM() {
    file.value.id3.popularimeter = null;
    id3POPMChange();
}


/*
    Saving and backend
*/

// Save to file
function save() {
    $1t.send('tagEditorSave', {
        changes: {
            path: file.value.path, 
            changes: changes.value,
            separators: {id3: ', ', vorbis: null, mp4: ', '},
            id3v24: id3v24.value
        }
    });
    changes.value = [];
}

function saveSettings() {
    $1t.settings.value.path = path.value;
    $1t.settings.value.tagEditorCustom = customList.value;
    $1t.saveSettings(false);
}

// Websocket callback
function wsCallback(e: any) {
    switch (e.action) {
        case 'browse':
            path.value = e.path;
            loadFiles();
            break;
        case 'tagEditorFolder':
            if (e.recursive) {
                // Add dir to custom list
                let files = customList.value.concat(e.files.sort((a: any, b: any) => {
                    return a.filename.toLowerCase().localeCompare(b.filename.toLowerCase());
                }).map((f: any) => f.path));
                // Deduplicate
                customList.value = [... new Set(files)];
            } else {
                path.value = e.path;
                //Dirs first and sort
                originalFiles.value = e.files.sort((a: any, b: any) => {
                    if (a.dir && !b.dir) return -1;
                    if (b.dir && !a.dir) return 1;
                    return a.filename.toLowerCase().localeCompare(b.filename.toLowerCase());
                });
                applyFilter(filter.value);
            }
            saveSettings();
            break;
        case 'tagEditorLoad':
            file.value = e.data;
            break;
        case 'tagEditorSave':
            $q.notify({
                message: 'Tags written!',
                timeout: 4000,
                position: 'top-right'
            });
            break;
        // Internal callback
        case '_tagEditorSave':
            save();
            break;
        default: 
            console.log(e);
            break;
    }
}

const tagFormat = computed(() => {
    if (!file.value) return null;
    if (file.value.format == 'flac' || file.value.format == 'ogg') return 'vorbis';
    if (file.value.format == 'mp4') return 'mp4';
    return 'id3';
});

// Filter used types
const albumArtTypes = computed(() => {
    let types = ["CoverFront", "CoverBack", "Other", "Artist", "Icon", "OtherIcon", 
        "Leaflet", "Media", "LeadArtist", "Conductor", "Band", "Composer", "Lyricist", 
        "RecordingLocation", "DuringRecording", "DuringPerformance", "ScreenCapture", 
        "BrightFish", "Illustration", "BandLogo", "PublisherLogo"];
    if (!file.value) return types;
    return types.filter((t) => file.value.images.find((i: any) => i.kind == t) ? false : true);
});

const POPMLabel = computed(() => {
    let v = file.value.id3.popularimeter.rating;
    let stars = Math.ceil(v / 51);
    if (stars == 0) stars = 1;
    return `${v} (${stars}⭐)`;
});

// Register callback
onMounted(() => {
    $1t.onTagEditorEvent = wsCallback;
    loadFiles();

    // Load QT track
    if ($1t.quickTag.value.toTagEditor) {
        loadFile($1t.quickTag.value.toTagEditor);
        $1t.quickTag.value.toTagEditor = undefined;
    } else if ($1t.quickTag.value.track.tracks.length == 1) {
        loadFile($1t.quickTag.value.track.tracks[0].path);
    }
})

// Unregister
onDeactivated(() => {
    $1t.onTagEditorEvent = () => {};
})

</script>

<style>
.te-file {
    padding: 2px;
    padding-left: 4px;
    border-radius: 8px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
}
.te-file:hover {
    background-color: #111312;
}
.path-display {
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    direction: rtl;
    text-align: left;
}
.albumart {
    min-width: 128px;
    width: 128px;
    max-width: 128px;
    border-radius: 8px;
}
.albumart-container {
    display: flex;
    width: 180px;
}
.separator {
    width: 2px; 
    margin-left: -17px; 
    position: absolute;
    height: 100%;
}
</style>