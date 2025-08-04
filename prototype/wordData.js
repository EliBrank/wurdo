const words = {
  "dark": {
    "anagram": {},
    "rhyme": {},
    "obo": { "dare": 20 },
  },

  "dare": {
    "anagram": {},
    "rhyme": { "flare": 15, "share": 15 },
    "obo": { "dark": 20 },
  },

  "flare": {
    "anagram": {},
    "rhyme": { "dare": 10, "share": 15 },
    "obo": { "flame": 30 },
  },

  "flame": {
    "anagram": {},
    "rhyme": { "same": 10, "shame": 15, "claim": 15 },
    "obo": { "flare": 30 },
  },

  "same": {
    "anagram": { "seam": 30 },
    "rhyme": { "flame": 15, "shame": 15, "claim": 15 },
    "obo": { "shame": 30 },
  },

  "shame": {
    "anagram": {},
    "rhyme": { "flame": 15, "same": 15, "claim": 15 },
    "obo": { "same": 20, "share": 30 },
  },

  "share": {
    "anagram": {},
    "rhyme": { "dare": 10, "flare": 15 },
    "obo": { "flame": 30, "shame": 30 },
  },

  "claim": {
    "anagram": {},
    "rhyme": { "flame": 15, "shame": 15, "same": 10 },
    "obo": {},
  },

  "clam": {
    "anagram": {},
    "rhyme": { "slam": 10 },
    "obo": { "clam": 20 },
  },

  "slam": {
    "anagram": {},
    "rhyme": { "clam": 10 },
    "obo": { "clam": 20 },
  },

  "seam": {
    "anagram": { "same": 30 },
    "rhyme": { "steam": 15, "stream": 20 },
    "obo": { "steam": 30 },
  },

  "steam": {
    "anagram": {},
    "rhyme": { "seam": 10, "stream": 25 },
    "obo": { "seam": 20, "stream": 40 },
  },

  "stream": {
    "anagram": { "master": 70 },
    "rhyme": { "steam": 15, "steam": 20 },
    "obo": { "steam": 15 },
  },

  "master": {
    "anagram": { "stream": 70 },
    "rhyme": { "faster": 20 },
    "obo": { "faster": 40 },
  },

  "faster": {
    "anagram": { "strafe": 70 },
    "rhyme": { "master": 20 },
    "obo": { "master": 40 },
  },

  "strafe": {
    "anagram": { "faster": 70 },
    "rhyme": {},
    "obo": { "strife": 40 },
  },

  "strife": {
    "anagram": {},
    "rhyme": { "life": 20 },
    "obo": { "strafe": 40 },
  },

  "life": {
    "anagram": { "file": 30 },
    "rhyme": {},
    "obo": { "live": 20 },
  },

  "live": {
    "anagram": {},
    "rhyme": {},
    "obo": { "life": 20, "vile": 20 },
  },

  "vile": {
    "anagram": { "live": 30 },
    "rhyme": { "file": 10 },
    "obo": { "file": 20 },
  },

  "file": {
    "anagram": { "life": 30 },
    "rhyme": { "vile": 10 },
    "obo": { "vile": 20 },
  },

  "film": {
    "anagram": {},
    "rhyme": {},
    "obo": { "file": 20 },
  },
}

export default words;
