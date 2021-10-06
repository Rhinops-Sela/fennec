import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DomainsLayoutComponent } from '../components/layout/domains-layout/domains-layout.component';
import { PagesLayoutComponent } from '../components/layout/pages-layout/pages-layout.component';
import { PageLayoutComponent } from '../components/layout/page-layout/page-layout.component';



const routes: Routes = [
  { path: '', component: DomainsLayoutComponent },
  { path: 'pages', component: PagesLayoutComponent },
  { path: 'page', component: PageLayoutComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
