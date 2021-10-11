import { IDomain } from '../../interfaces/common/IDomain';
import { Injectable } from '@angular/core';
import { IPage } from 'src/app/interfaces/common/IPage';
import { IInput } from 'src/app/interfaces/common/IInput';
import { of, Subject } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { Form, FormGroup } from '@angular/forms';
import { BackendService } from '../backend/backend.service';
import { GUID } from 'src/app/helpers/guid';
import { IRefreshRequried } from 'src/app/interfaces/client/IRefreshRequried';
import { MessageHandlerService } from '../message-handler/message-handler.service';
import { FileSelectionDialogComponent } from 'src/app/components/dialogs/file-selection-dialog/file-selection-dialog.component';
import { S3Service } from '../s3/s3.service';
import { S3LoginComponent } from 'src/app/components/dialogs/s3-login-dialog/s3-login.component';
import { ProgressSpinnerComponent } from 'src/app/components/progress-spinner/progress-spinner.component';
import { ProgressHandlerService } from '../progress-handler/progress-handler.service';
@Injectable({
  providedIn: 'root',
})
export class GlobalService {
  private activeDomain: IDomain;
  private activePage: IPage;
  public refreshRequired: Subject<IRefreshRequried> = new Subject<
    IRefreshRequried
  >();
  private allDomains: IDomain[];
  constructor(
    private s3Service: S3Service,
    private backendService: BackendService,
    private errorHandlerService: MessageHandlerService,
    private messageHandlerService: MessageHandlerService,
    public dialog: MatDialog,
    private progressHandlerService: ProgressHandlerService
  ) {}

  public async getAllDomains(): Promise<IDomain[]> {
    if (!this.allDomains) {
      await this.loadDomains();
    }
    return this.allDomains;
  }

  public async getModifiedList(single:string = ""): Promise<IDomain[]> {
    const modifiedList: IDomain[] = [];
    const domainList: IDomain[] = await this.getAllDomains();
    for (const domain of domainList) {
      const domainClone = JSON.parse(JSON.stringify(domain)) as IDomain;
      const pages = domainClone.pages.filter((page) => {
        if(single){
          return page.modified === true && page.name == single || page.name == 'cluster';  
        }
        return page.modified === true;
      });
      domainClone.pages = pages;
      if (pages.length > 0) {
        modifiedList.push(domainClone);
      }
    }
    return modifiedList;
  }

  private async loadDomains() {
    if (!this.loadFromLocalStorage()) {
      this.allDomains = await this.backendService.getFormTemplate();
      this.setGuids();
    }
  }

  private setGuids() {
    this.allDomains.forEach((domain) => {
      domain.id = GUID();
      domain.pages.forEach((page) => {
        page.id = GUID();
        page.inputs.forEach((input) => {
          input.id = GUID();
        });
      });
    });
  }

  private loadFromLocalStorage(): boolean {
    const storedForm = this.getLocalStorageForm();
    if (!storedForm) {
      return false;
    }
    this.allDomains = JSON.parse(storedForm);
    this.allDomains.forEach((domain) => {
      let icon = '';
      domain.pages.forEach((page) => {
        if (page.valid && page.inputs[0].value) {
          icon = 'done';
        }
      });
      domain.icon = icon;
    });
    return true;
  }

  public async clearAll() {
    localStorage.clear();
    await this.loadDomains();
    this.refreshRequired.next({ pageChanged: false, domainChanged: true });
    return true;
  }
  public uploadForm(jsonForm: string) {
    try {
      this.allDomains = JSON.parse(jsonForm);
      this.setGuids();
      this.storeLocalStorage(this.allDomains);
      return { result: true };
    } catch (error) {
      this.errorHandlerService.onErrorOccured.next(
        `Failed to upload file: ${error.message}`
      );
      return false;
    }
  }

  private getLocalStorageForm() {
    const form = localStorage.getItem('storedForm');
    return form;
  }
  private getLocalStorageDomain() {
    const domain = localStorage.getItem('activeDomain');
    return domain;
  }

  private storeLocalStorage(storedForm?: IDomain[], activeDomain?: IDomain) {
    let refresh = false;
    if (storedForm) {
      localStorage.setItem('storedForm', JSON.stringify(storedForm));
      refresh = true;
    }
    if (activeDomain) {
      refresh = true;
      localStorage.setItem('activeDomain', JSON.stringify(activeDomain));
    }
  }

  private deleteLocalStorage(storedForm = false, activeDomain = false) {
    if (storedForm) {
      localStorage.removeItem('storedForm');
    }
    if (activeDomain) {
      localStorage.removeItem('activeDomain');
    }
    this.activeDomain = null;
    this.activePage = null;
  }

  public savePage(modifiedPage: IPage, form?: FormGroup) {
    const pageToModify = this.activeDomain.pages.find(
      (page) => page.id === modifiedPage.id
    );
    if (form) {
      pageToModify.inputs.forEach((input) => {
        if (form.controls[input.id]) {
          input.value = form.controls[input.id].value;
        } else {
          if (input.controlType == "checkbox") {
            input.value = false;
          }
        }
      });
      pageToModify.modified = true;
      pageToModify.icon = 'check_box'
     // this.setPageIcon(true);
    } else {
      pageToModify.inputs = modifiedPage.inputs;
      pageToModify.modified = false;
      if (pageToModify.mandatory) {
         pageToModify.icon = 'priority_high';
      } else {
         pageToModify.icon = 'check_box_outline_blank';
      }
     // this.setPageIcon(false);
    }
    this.storeLocalStorage(this.allDomains, this.activeDomain);
    this.refreshRequired.next({ pageChanged: true, domainChanged: true });
  }

  public saveDomain(modifiedDomain: IDomain) {
    modifiedDomain.valid = true;
    for (let i = 0; i < this.allDomains.length; i++) {
      if (this.allDomains[i].id === modifiedDomain.id) {
        this.allDomains[i] = modifiedDomain;
        this.storeLocalStorage(this.allDomains);
        return;
      }
    }
  }

  public verifyMandatory(): IPage[] {
    const notValidMandatory: IPage[] = [];
    this.allDomains.forEach((domain) => {
      domain.pages.forEach((page) => {
        if (page.mandatory && !page.modified) {
          notValidMandatory.push(page);
        }
      });
    });

    return notValidMandatory;
  }

  public setPageIcon(valid: boolean) {
    if (valid) {
      this.activePage.icon = 'done';
    } else {
      this.activePage.icon = '';
    }
    // this.saveDomain(this.activeDomain);
    this.savePage(this.activePage);
    //this.refreshRequired.next({ pageChanged: true, domainChanged: true });
  }

  public resetPage(page: IPage) {
    this.activeDomain.icon = '';
    this.activeDomain.modified = false;
    this.saveDomain(this.activeDomain);
    page.modified = false;
    page.inputs.forEach((input) => {
      input.value = '';
    });
    this.savePage(page);
    this.refreshRequired.next({ pageChanged: true, domainChanged: false });
  }

  public clonePage(pageSource: IPage) {
    const newPage = JSON.parse(JSON.stringify(pageSource)) as IPage;
    newPage.id = GUID();
    newPage.inputs.forEach((input) => {
      input.id = GUID();
    });
    this.setClonedName(newPage);
    const index = this.activeDomain.pages.findIndex(
      (page) => page.id === pageSource.id
    );
    this.activeDomain.pages.splice(index + 1, 0, newPage);
    this.storeLocalStorage(null, this.activeDomain);
    this.saveDomain(this.activeDomain);
    this.refreshRequired.next({ pageChanged: true, domainChanged: true });
  }

  private setClonedName(newPage: IPage) {
    let suffix = `fenneccloned${GUID()}`;
    const split = newPage.name.split('_');
    const splitLast = split[split.length - 1];
    if (splitLast.indexOf('fenneccloned') > -1) {
      newPage.name = newPage.name.replace(splitLast, suffix);;
    } else {
      newPage.name += `_${suffix}`;
    }
  }

  public deletePage(pageSource: IPage) {
    const index = this.activeDomain.pages.findIndex(
      (page) => page.id === pageSource.id
    );
    this.activeDomain.pages.splice(index, 1);
    this.storeLocalStorage(null, this.activeDomain);
    this.saveDomain(this.activeDomain);
    this.refreshRequired.next({ pageChanged: true, domainChanged: true });
  }

  public canDelete(pageToCheck: IPage): boolean {
    if (!this.activeDomain) {
      this.allDomains.forEach((domain) => {
        const workingPage = domain.pages.find(
          (page) => page.displayName === pageToCheck.displayName
        );
        if (workingPage) {
          this.activeDomain = domain;
        }
      });
    }
    const domainPages = this.activeDomain.pages.filter(
      (page) => page.displayName === pageToCheck.displayName
    );
    return domainPages.length > 1;
  }

  public getInputs(page: IPage): any {
    const pageInputs: IInput[] = [];
    page.inputs.forEach((input: IInput) => {
      pageInputs.push(input);
    });
    return of(pageInputs);
  }

  public onDomainChange(activeDomain: IDomain, selectedPage?: IPage) {
    this.activeDomain = activeDomain;
    this.storeLocalStorage(null, activeDomain);
    this.activePage = selectedPage || activeDomain.pages[0];
    this.refreshRequired.next({ pageChanged: true, domainChanged: true });
  }

  public onPageChange(activePage: IPage, activeDomain?: IDomain) {
    this.activePage = activePage;
    if (activeDomain && activeDomain !== this.activeDomain) {
      this.onDomainChange(activeDomain, activePage);
    } else {
      this.refreshRequired.next({ pageChanged: true, domainChanged: false });
    }
  }

  public getActivePage(): IPage {
    return this.activePage;
  }

  public getActiveDomain(): IDomain {
    const fromStorage = JSON.parse(this.getLocalStorageDomain());
    const result = fromStorage || this.activeDomain;
    return result;
  }

  public resetActiveDomainText() {
    this.activeDomain = null;
    this.deleteLocalStorage(false, true);
  }

  async export(domainsToExport?: IDomain[], s3: boolean = true) {
    const dialogRef = this.dialog.open(FileSelectionDialogComponent, {
      data: {
        s3: s3,
      },
    });
    const dialogResult = await dialogRef.afterClosed().toPromise();
    if (!dialogResult || !dialogResult.filename) {
      return;
    }
    let filename = dialogResult.filename;
    if (filename.indexOf('.json') == -1) {
      filename += '.json';
    }
    if (dialogResult.exportDesitination == 'local') {
      await this.exportLocal(filename, domainsToExport);
    } else {
      this.storeToS3(filename);
    }
  }

  public async storeToS3(filename?: string) {
    this.dialog.open(ProgressSpinnerComponent, {
      data: {
        header: 'Uploading Files To S3 Bucket',
        subheader: 'Storing files on S3 bucket',
      },
      disableClose: true,
    });
    let upload = false;
    const loadedCredentials = await this.s3Service.isCredentialsLoaded();

    if (!loadedCredentials) {
      const dialogRef = this.dialog.open(S3LoginComponent, {
        disableClose: true,
      });
      const dialogResult = await dialogRef.afterClosed().toPromise();
      if (dialogResult?.response) {
        upload = true;
      }
    } else {
      upload = true;
    }
    if (upload) {
      try {
        await this.uploadBeforeDeployment(filename);
        this.messageHandlerService.onUserMessage.next(
          'File Was Successfuly Uploaded'
        );
      } catch (error) {
        this.messageHandlerService.onErrorOccured.next(
          `Failed to save to S3 bucket: ${error.message}`
        );
      }
    }
    this.progressHandlerService.onActionCompleted.next(true);
  }

  private async uploadBeforeDeployment(filename: string) {
    const allDomains = await this.getAllDomains();
    await this.s3Service.uploadForm(JSON.stringify(allDomains), filename);
  }

  async exportLocal(filename: string, domainsToExport?: IDomain[]) {
    try {
      let form = domainsToExport || (await this.getAllDomains());
      const domains = form;
      const jsonFormat = JSON.stringify(domains);
      const blob = new Blob([jsonFormat], {
        type: 'text/plain;charset=utf-8',
      });
      saveAs(blob, filename);
    } catch (error) {
      this.messageHandlerService.onErrorOccured.next(
        `Export failed: ${error.message}`
      );
    }
  }
}
