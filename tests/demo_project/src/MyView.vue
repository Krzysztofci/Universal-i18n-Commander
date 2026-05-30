<!-- TEST FILE: src/MyView.vue -->
<!-- Pokrywa wzorzec: {{ $t("klucz") }} -->

<template>
  <div>
    <!-- OCZEKIWANE OK (plugin: dollar_t) -->
    <h1>{{ $t("KEY_OK_DOLLAR_T") }}</h1>

    <!-- OCZEKIWANE OK (plugin: dollar_t) — z pojedynczym cudzysłowem -->
    <p>{{ $t('KEY_OK_SINGLE_QUOTE') }}</p>

    <!-- PUŁAPKA: klucz w komentarzu HTML — NIE powinien być zliczany -->
    <!-- {{ $t("KEY_GHOST_COMMENT_ONLY") }} -->

    <!-- PUŁAPKA: klucz jako tekst, bez $t() -->
    <span>KEY_GHOST_STRING_LITERAL</span>
  </div>
</template>
