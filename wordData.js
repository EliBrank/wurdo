const words = {
  "dark": {
    "obo": { "dare": 20 },
    "rhyme": {},
    "anagram": {}
  },

  "dare": {
    "obo": { "dark": 20 },
    "rhyme": { "flare": 15 },
    "anagram": {}
  },

  "flare": {
    "obo": { "flame": 30 },
    "rhyme": { "dare": 10, "share": 15 },
    "anagram": {}
  },

  "flame": {
    "obo": { "flare": 30 },
    "rhyme": { "same": 10, "shame": 15, "claim": 15 },
    "anagram": {}
  },

  "same": {
    "obo": { "shame": 30 },
    "rhyme": { "flame": 15, "shame": 15, "claim": 15 },
    "anagram": {}
  },

  "shame": {
    "obo": { "same": 20, "share": 30 },
    "rhyme": { "flame": 15, "same": 15, "claim": 15 },
    "anagram": {}
  },

  "share": {
    "obo": { "flame": 30, "shame": 30 },
    "rhyme": { "flare": 15 },
    "anagram": {}
  },

  "claim": {
    "obo": { "dare": 12 },
    "rhyme": { "flame": 15, "shame": 15, "same": 10 },
    "anagram": {}
  },

  "clam": {
    "obo": { "clam": 20 },
    "rhyme": { "slam": 10 },
    "anagram": {}
  },

  "slam": {
    "obo": { "clam": 20 },
    "rhyme": { "clam": 10 },
    "anagram": {}
  },

  "seam": {
    "obo": { "steam": 30 },
    "rhyme": { "steam": 15, "stream": 20 },
    "anagram": {}
  },

  "steam": {
    "obo": { "seam": 20, "stream": 40 },
    "rhyme": { "seam": 10, "stream": 25 },
    "anagram": {}
  },

  "stream": {
    "obo": { "steam": 15 },
    "rhyme": { "steam": 15, "steam": 20 },
    "anagram": { "master": 70 }
  },

  "master": {
    "obo": { "faster": 40 },
    "rhyme": { "faster": 20 },
    "anagram": { "stream": 70 }
  },

  "faster": {
    "obo": { "master": 40 },
    "rhyme": { "master": 20 },
    "anagram": { "strafe": 70 }
  },

  "strafe": {
    "obo": { "strife": 40 },
    "rhyme": {},
    "anagram": { "faster": 70 }
  },

  "strife": {
    "obo": { "strafe": 40 },
    "rhyme": { "life": 20 },
    "anagram": {}
  },

  "life": {
    "obo": { "live": 20 },
    "rhyme": {},
    "anagram": { "file": 30 }
  },

  "live": {
    "obo": { "life": 20, "vile": 20 },
    "rhyme": {},
    "anagram": {}
  },

  "vile": {
    "obo": { "file": 20 },
    "rhyme": { "file": 10 },
    "anagram": { "live": 30 }
  },

  "file": {
    "obo": { "vile": 20 },
    "rhyme": { "vile": 10 },
    "anagram": { "life": 30 }
  },

  "film": {
    "obo": { "file": 20 },
    "rhyme": {},
    "anagram": {}
  },
}

export default words;
