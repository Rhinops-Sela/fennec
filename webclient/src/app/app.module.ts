import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './modules/app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { FlexLayoutModule } from '@angular/flex-layout';
import { DemoMaterialModule } from './modules/material.module';
import { HttpClientModule } from '@angular/common/http';
import { MAT_FORM_FIELD_DEFAULT_OPTIONS } from '@angular/material/form-field';
import { LayoutModule } from '@angular/cdk/layout';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

import { MatProgressBarModule } from '@angular/material/progress-bar';

import { ProgressSpinnerComponent } from './components/progress-spinner/progress-spinner.component';
import { FileSelectionDialogComponent } from './components/dialogs/file-selection-dialog/file-selection-dialog.component';
import { DomainsLayoutComponent } from './components/layout/domains-layout/domains-layout.component';
import { SideNavComponent } from './components/layout/sidenav-layout/side-nav.component';
import { InputComponentComponent } from './components/inputs/input-component.component';
import { PageLayoutComponent } from './components/layout/page-layout/page-layout.component';
import { ToolbarComponent } from './components/layout/toolbar-layout/toolbar-layout.component';
import { PagesLayoutComponent } from './components/layout/pages-layout/pages-layout.component';
import { ConfirmationModalComponent } from './components/dialogs/deployment-confirmation-dialog/confirmation-modal.component';
import { CommandButtonsComponent } from './components/layout/command-buttons-layout/command-buttons.component';
import { DeploymentProgressModalComponent } from './components/dialogs/deplopyment-progress-modal/deployment-progress-modal.component';
import { BrowseStoredFilesComponent } from './components/dialogs/browse-stored-files-dialog/browse-stored-files.component';
import { S3LoginComponent } from './components/dialogs/s3-login-dialog/s3-login.component';
import { ConfirmDialogComponent } from './components/dialogs/confirm-dialog/confirm-dialog.component';
// import { FileSelectDirective } from 'ng2-file-upload';
@NgModule({
  declarations: [
    AppComponent,
    DomainsLayoutComponent,
    SideNavComponent,
    InputComponentComponent,
    PageLayoutComponent,
    ToolbarComponent,
    PagesLayoutComponent,
    ConfirmationModalComponent,
    CommandButtonsComponent,
    DeploymentProgressModalComponent,
    BrowseStoredFilesComponent,
    S3LoginComponent,
    ProgressSpinnerComponent,
    FileSelectionDialogComponent,
    ConfirmDialogComponent
  ],
  imports: [
    FontAwesomeModule,
    FormsModule,
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    DemoMaterialModule,
    ReactiveFormsModule,
    HttpClientModule,
    DemoMaterialModule,
    FlexLayoutModule,
    LayoutModule,
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatIconModule,
    MatListModule,
    MatProgressBarModule,
  ],
  providers: [
    {
      provide: MAT_FORM_FIELD_DEFAULT_OPTIONS,
      useValue: { appearance: 'fill' },
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
