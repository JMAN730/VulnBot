import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { subscribeUiPreferences } from "../utils/preferences";
import en from "./en.json";

type Lang = "en-US";
type Translations = Record<string, string>;
export type TFunction = (key: string, params?: Record<string, string>, fallback?: string) => string;

const TRANSLATIONS: Record<Lang, Translations> = {
  "en-US": en as Translations,
};

let _currentLang: Lang = "en-US";
let _currentTranslations: Translations = TRANSLATIONS[_currentLang];

export function t(key: string, params?: Record<string, string>, fallback?: string): string {
  let text = _currentTranslations[key];
  if (text === undefined) {
    text = TRANSLATIONS["en-US"][key];
  }
  if (text === undefined) {
    text = fallback ?? key;
  }
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      text = text.replace(`{${k}}`, String(v));
    }
  }
  return text;
}

interface I18nContextValue {
  lang: Lang;
  t: (key: string, params?: Record<string, string>, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextValue>({
  lang: _currentLang,
  t,
});

export function useT(): I18nContextValue {
  return useContext(I18nContext);
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(_currentLang);

  useEffect(() => {
    const unsubscribe = subscribeUiPreferences(() => {
      if (_currentLang !== "en-US") {
        _currentLang = "en-US";
        _currentTranslations = TRANSLATIONS["en-US"];
        setLang("en-US");
      }
    });
    return unsubscribe;
  }, []);

  const value = useMemo<I18nContextValue>(() => {
    const tFn: TFunction = (key, params, fallback) => {
      let text = TRANSLATIONS[lang][key];
      if (text === undefined) text = fallback ?? key;
      if (params) {
        for (const [k, v] of Object.entries(params)) text = text.replace(`{${k}}`, String(v));
      }
      return text;
    };
    return { lang, t: tFn };
  }, [lang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
