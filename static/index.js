(function(){
  const I18N = {
    zh: {
      title: "妙妙小工具入口",
      subtitle: "把常用的小工具都放在这里，一键进入。"
    },
    en: {
      title: "Portal of Handy Tools",
      subtitle: "Collect frequently used mini-apps here, one click to open."
    }
  };

  function getLang(){ return localStorage.getItem('portal_lang') || 'zh'; }
  function setLang(lang){
    localStorage.setItem('portal_lang', lang);
    applyLang(lang);
  }
  function applyLang(lang){
    const dict = I18N[lang] || I18N.zh;
    document.getElementById('titleText').textContent = dict.title;
    document.getElementById('subtitleText').textContent = dict.subtitle;
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    applyLang(getLang());
    document.getElementById('langToggle').addEventListener('click', ()=>{
      setLang(getLang()==='zh' ? 'en' : 'zh');
    });
  });
})();
