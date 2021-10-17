import { enableProdMode } from '@angular/core';
import { environment, setEnvironnement } from './environments/environment';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
fetch('/assets/config.json')
  .then(response => response.json())
  .then((data: any) => {
    setEnvironnement(data);

 //   if (environment.environmentType !== EnvironmentType.Local) {
      enableProdMode();
 //   }

    platformBrowserDynamic().bootstrapModule(AppModule)
      .catch(err => console.error(err));

  });