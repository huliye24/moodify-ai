// Mock data for Moodify Workspace
// 20 audio assets with AI analysis

export interface AudioAsset {
  id: string
  title: string
  artist: string
  genre: string
  mood: string
  duration: number
  mrs: {
    overall: number
    fidelity: number
    balance: number
    clarity: number
  }
  analysis: {
    tempo: number
    energy: number
    emotion: string
    frequencyBalance: string
    stereoWidth: number
  }
  status: 'analyzed' | 'processing' | 'pending'
  lastModified: string
  tags: string[]
}

export const mockAssets: AudioAsset[] = [
  {
    id: '1',
    title: 'Midnight Dreams',
    artist: 'Luna Collective',
    genre: 'Ambient',
    mood: 'Melancholic',
    duration: 245,
    mrs: { overall: 86, fidelity: 88, balance: 84, clarity: 85 },
    analysis: { tempo: 72, energy: 45, emotion: 'Contemplative', frequencyBalance: 'Good', stereoWidth: 0.82 },
    status: 'analyzed',
    lastModified: '2026-08-20',
    tags: ['ambient', 'chill', 'night']
  },
  {
    id: '2',
    title: 'Electric Pulse',
    artist: 'Neon Systems',
    genre: 'Electronic',
    mood: 'Energetic',
    duration: 198,
    mrs: { overall: 92, fidelity: 94, balance: 90, clarity: 93 },
    analysis: { tempo: 128, energy: 89, emotion: 'Excited', frequencyBalance: 'Excellent', stereoWidth: 0.91 },
    status: 'analyzed',
    lastModified: '2026-08-19',
    tags: ['electronic', 'dance', 'upbeat']
  },
  {
    id: '3',
    title: 'Urban Echoes',
    artist: 'City Sounds',
    genre: 'Hip Hop',
    mood: 'Urban',
    duration: 215,
    mrs: { overall: 78, fidelity: 76, balance: 80, clarity: 77 },
    analysis: { tempo: 95, energy: 72, emotion: 'Confident', frequencyBalance: 'Fair', stereoWidth: 0.75 },
    status: 'analyzed',
    lastModified: '2026-08-18',
    tags: ['hiphop', 'urban', 'beats']
  },
  {
    id: '4',
    title: 'Ocean Waves',
    artist: 'Nature Recordings',
    genre: 'Nature',
    mood: 'Peaceful',
    duration: 360,
    mrs: { overall: 94, fidelity: 95, balance: 93, clarity: 94 },
    analysis: { tempo: 0, energy: 12, emotion: 'Tranquil', frequencyBalance: 'Excellent', stereoWidth: 0.88 },
    status: 'analyzed',
    lastModified: '2026-08-17',
    tags: ['nature', 'ambient', 'relaxation']
  },
  {
    id: '5',
    title: 'Jazz Lounge',
    artist: 'Smooth Quartet',
    genre: 'Jazz',
    mood: 'Sophisticated',
    duration: 280,
    mrs: { overall: 88, fidelity: 87, balance: 89, clarity: 88 },
    analysis: { tempo: 110, energy: 55, emotion: 'Relaxed', frequencyBalance: 'Good', stereoWidth: 0.79 },
    status: 'analyzed',
    lastModified: '2026-08-16',
    tags: ['jazz', 'lounge', 'sophisticated']
  },
  {
    id: '6',
    title: 'Rock Anthem',
    artist: 'Thunder Band',
    genre: 'Rock',
    mood: 'Powerful',
    duration: 195,
    mrs: { overall: 82, fidelity: 80, balance: 84, clarity: 81 },
    analysis: { tempo: 145, energy: 95, emotion: 'Intense', frequencyBalance: 'Good', stereoWidth: 0.85 },
    status: 'analyzed',
    lastModified: '2026-08-15',
    tags: ['rock', 'anthem', 'power']
  },
  {
    id: '7',
    title: 'Classical Piano',
    artist: 'Virtuoso',
    genre: 'Classical',
    mood: 'Elegant',
    duration: 420,
    mrs: { overall: 96, fidelity: 97, balance: 95, clarity: 96 },
    analysis: { tempo: 72, energy: 35, emotion: 'Serene', frequencyBalance: 'Excellent', stereoWidth: 0.92 },
    status: 'analyzed',
    lastModified: '2026-08-14',
    tags: ['classical', 'piano', 'elegant']
  },
  {
    id: '8',
    title: 'Synthwave Dreams',
    artist: 'Retro Future',
    genre: 'Synthwave',
    mood: 'Nostalgic',
    duration: 225,
    mrs: { overall: 89, fidelity: 88, balance: 90, clarity: 89 },
    analysis: { tempo: 118, energy: 78, emotion: 'Dreamy', frequencyBalance: 'Good', stereoWidth: 0.87 },
    status: 'analyzed',
    lastModified: '2026-08-13',
    tags: ['synthwave', 'retro', '80s']
  },
  {
    id: '9',
    title: 'Acoustic Session',
    artist: 'Guitar Stories',
    genre: 'Acoustic',
    mood: 'Warm',
    duration: 185,
    mrs: { overall: 91, fidelity: 92, balance: 90, clarity: 91 },
    analysis: { tempo: 85, energy: 48, emotion: 'Warm', frequencyBalance: 'Excellent', stereoWidth: 0.76 },
    status: 'analyzed',
    lastModified: '2026-08-12',
    tags: ['acoustic', 'guitar', 'warm']
  },
  {
    id: '10',
    title: 'Deep House',
    artist: 'Underground',
    genre: 'House',
    mood: 'Hypnotic',
    duration: 380,
    mrs: { overall: 84, fidelity: 83, balance: 85, clarity: 84 },
    analysis: { tempo: 124, energy: 82, emotion: 'Focused', frequencyBalance: 'Good', stereoWidth: 0.89 },
    status: 'analyzed',
    lastModified: '2026-08-11',
    tags: ['house', 'deep', 'electronic']
  },
  {
    id: '11',
    title: 'Cinematic Score',
    artist: 'Film Composer',
    genre: 'Cinematic',
    mood: 'Epic',
    duration: 295,
    mrs: { overall: 93, fidelity: 94, balance: 92, clarity: 93 },
    analysis: { tempo: 68, energy: 88, emotion: 'Epic', frequencyBalance: 'Excellent', stereoWidth: 0.94 },
    status: 'analyzed',
    lastModified: '2026-08-10',
    tags: ['cinematic', 'epic', 'orchestral']
  },
  {
    id: '12',
    title: 'Lo-Fi Study',
    artist: 'Chill Beats',
    genre: 'Lo-Fi',
    mood: 'Focused',
    duration: 165,
    mrs: { overall: 79, fidelity: 77, balance: 81, clarity: 78 },
    analysis: { tempo: 82, energy: 32, emotion: 'Calm', frequencyBalance: 'Fair', stereoWidth: 0.71 },
    status: 'analyzed',
    lastModified: '2026-08-09',
    tags: ['lofi', 'study', 'chill']
  },
  {
    id: '13',
    title: 'Techno Drive',
    artist: 'Industrial',
    genre: 'Techno',
    mood: 'Driving',
    duration: 340,
    mrs: { overall: 87, fidelity: 86, balance: 88, clarity: 87 },
    analysis: { tempo: 138, energy: 94, emotion: 'Intense', frequencyBalance: 'Good', stereoWidth: 0.86 },
    status: 'analyzed',
    lastModified: '2026-08-08',
    tags: ['techno', 'industrial', 'driving']
  },
  {
    id: '14',
    title: 'Soul Ballad',
    artist: 'Velvet Voice',
    genre: 'Soul',
    mood: 'Emotional',
    duration: 255,
    mrs: { overall: 90, fidelity: 91, balance: 89, clarity: 90 },
    analysis: { tempo: 68, energy: 58, emotion: 'Passionate', frequencyBalance: 'Excellent', stereoWidth: 0.83 },
    status: 'analyzed',
    lastModified: '2026-08-07',
    tags: ['soul', 'ballad', 'emotional']
  },
  {
    id: '15',
    title: 'Folk Tales',
    artist: 'Storyteller',
    genre: 'Folk',
    mood: 'Storytelling',
    duration: 210,
    mrs: { overall: 85, fidelity: 84, balance: 86, clarity: 85 },
    analysis: { tempo: 92, energy: 45, emotion: 'Nostalgic', frequencyBalance: 'Good', stereoWidth: 0.74 },
    status: 'analyzed',
    lastModified: '2026-08-06',
    tags: ['folk', 'story', 'acoustic']
  },
  {
    id: '16',
    title: 'Metal Crusher',
    artist: 'Heavy Metal',
    genre: 'Metal',
    mood: 'Aggressive',
    duration: 205,
    mrs: { overall: 81, fidelity: 79, balance: 83, clarity: 80 },
    analysis: { tempo: 165, energy: 98, emotion: 'Aggressive', frequencyBalance: 'Fair', stereoWidth: 0.88 },
    status: 'analyzed',
    lastModified: '2026-08-05',
    tags: ['metal', 'heavy', 'aggressive']
  },
  {
    id: '17',
    title: 'Reggae Vibes',
    artist: 'Island Sound',
    genre: 'Reggae',
    mood: 'Relaxed',
    duration: 235,
    mrs: { overall: 83, fidelity: 82, balance: 84, clarity: 83 },
    analysis: { tempo: 78, energy: 62, emotion: 'Laid-back', frequencyBalance: 'Good', stereoWidth: 0.77 },
    status: 'analyzed',
    lastModified: '2026-08-04',
    tags: ['reggae', 'island', 'relaxed']
  },
  {
    id: '18',
    title: 'Pop Hit',
    artist: 'Star Maker',
    genre: 'Pop',
    mood: 'Catchy',
    duration: 188,
    mrs: { overall: 88, fidelity: 87, balance: 89, clarity: 88 },
    analysis: { tempo: 122, energy: 86, emotion: 'Happy', frequencyBalance: 'Good', stereoWidth: 0.84 },
    status: 'analyzed',
    lastModified: '2026-08-03',
    tags: ['pop', 'catchy', 'radio']
  },
  {
    id: '19',
    title: 'World Fusion',
    artist: 'Global Sounds',
    genre: 'World',
    mood: 'Exotic',
    duration: 270,
    mrs: { overall: 86, fidelity: 85, balance: 87, clarity: 86 },
    analysis: { tempo: 105, energy: 68, emotion: 'Mysterious', frequencyBalance: 'Good', stereoWidth: 0.90 },
    status: 'analyzed',
    lastModified: '2026-08-02',
    tags: ['world', 'fusion', 'ethnic']
  },
  {
    id: '20',
    title: 'Experimental',
    artist: 'Avant Garde',
    genre: 'Experimental',
    mood: 'Abstract',
    duration: 310,
    mrs: { overall: 75, fidelity: 73, balance: 77, clarity: 74 },
    analysis: { tempo: 0, energy: 42, emotion: 'Abstract', frequencyBalance: 'Fair', stereoWidth: 0.95 },
    status: 'analyzed',
    lastModified: '2026-08-01',
    tags: ['experimental', 'avant-garde', 'abstract']
  },
]

// Dashboard stats
export const dashboardStats = {
  totalTracks: mockAssets.length,
  analyzedTracks: mockAssets.filter(a => a.status === 'analyzed').length,
  averageMRS: Math.round(mockAssets.reduce((sum, a) => sum + a.mrs.overall, 0) / mockAssets.length),
  recentAnalyses: mockAssets.slice(0, 5),
}

// Genre distribution
export const genreDistribution = [
  { genre: 'Electronic', count: 4 },
  { genre: 'Ambient', count: 2 },
  { genre: 'Rock', count: 2 },
  { genre: 'Jazz', count: 1 },
  { genre: 'Classical', count: 1 },
  { genre: 'Hip Hop', count: 1 },
  { genre: 'Other', count: 9 },
]
