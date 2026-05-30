// TEST FILE: src/Component.jsx
// Pokrywa wzorzec: t("klucz"), i18n.t("klucz")

import { useTranslation } from 'react-i18next';

function MyComponent() {
    const { t } = useTranslation();

    // OCZEKIWANE OK (plugin: t_fn)
    const title = t("KEY_OK_T_FN");

    // OCZEKIWANE OK (plugin: t_fn) — przez i18n.t
    const sub = i18n.t("KEY_OK_DOUBLE_QUOTE");

    // PUŁAPKA: klucz jako plain string w JSX
    const raw = "KEY_GHOST_STRING_LITERAL";

    // PUŁAPKA: w komentarzu
    // t("KEY_GHOST_COMMENT_ONLY")

    return (
        <div>
            <h1>{title}</h1>
            <p>{sub}</p>
        </div>
    );
}
