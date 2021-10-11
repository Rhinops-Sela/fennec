import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { GlobalService } from 'src/app/services/global/global.service';
import { IPage } from 'src/app/interfaces/common/IPage';
import { FormService } from 'src/app/services/form/form.service';
import { Router } from '@angular/router';
import { IRefreshRequried } from 'src/app/interfaces/client/IRefreshRequried';
import { ConfirmDialogComponent } from '../../dialogs/confirm-dialog/confirm-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { IInput } from 'src/app/interfaces/common/IInput';
import { group } from 'console';
import { IDomain } from 'src/app/interfaces/common/IDomain';
import { DeploymentProgressModalComponent } from '../../dialogs/deplopyment-progress-modal/deployment-progress-modal.component';
import { DeploymentService } from 'src/app/services/deployment/deployment.service';
import { FileSelectionDialogComponent } from '../../dialogs/file-selection-dialog/file-selection-dialog.component';
@Component({
  selector: 'app-page-component',
  templateUrl: './page-layout.component.html',
  styleUrls: ['./page-layout.component.scss'],
})
export class PageLayoutComponent implements OnInit {
  form: FormGroup;
  page: IPage;

  constructor(
    public formService: FormService,
    private globalService: GlobalService,
    private router: Router,
    public dialog: MatDialog,
    private deploymentService: DeploymentService,
  ) {}

  ngOnInit(): void {
    this.page = this.globalService.getActivePage();
    if (!this.page || !this.page.inputs) {
      this.router.navigate(['']);
    }
    this.globalService.refreshRequired.subscribe((result: IRefreshRequried) => {
      if (result.pageChanged) {
        this.page = this.globalService.getActivePage();
        this.form = new FormGroup({});
        this.form = this.formService.appendToFormGroup(
          this.page.inputs,
          this.form
        );
      }
    });
    this.loadPage();
  }

  private loadPage() {
    this.page = this.globalService.getActivePage();
    if (!this.page || !this.page.inputs) {
      this.router.navigate(['']);
    } else {
      this.form = this.formService.appendToFormGroup(
        this.page.inputs,
        this.form
      );
    }
  }
  onSubmit() {
    this.globalService.savePage(this.page, this.form);
    // this.globalService.setPageIcon(true);
    this.router.navigate(['pages']);
  }

  onCancel() {
    this.router.navigate(['pages']);
  }

  onDelete() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        header: 'Delete Component?',
        content: 'Are you sure you wish to delete the component?',
        confrimButtonText: 'Delete',
      },
    });
    dialogRef.afterClosed().subscribe((result) =>  {
      if (result) {
        this.globalService.savePage(this.page, this.form);
        this.globalService.getModifiedList(this.page.name).then(domainList => {
          
          this.openProgressDialog(domainList,true)
        })
        
        
      }
    });
  }

  private openProgressDialog(domainsToInstall: IDomain[], deleteMode: boolean) {
    const dialogRef = this.dialog.open(DeploymentProgressModalComponent, {
      data: { domains: domainsToInstall, deleteMode: deleteMode },
      disableClose: true,
    });
    const deploymentService = this.deploymentService;
    dialogRef.afterClosed().subscribe((result: any) => {
      console.log(result);
      deploymentService.closeSocket();
      this.form.reset();
      this.globalService.resetPage(this.page);
      this.globalService.export()
    });
  }

  onReset() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        header: 'Reset Page Data?',
        content: 'Are you sure you wish to reset page data?',
        confrimButtonText: 'Reset',
      },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.form.reset();
        this.globalService.resetPage(this.page);
      }
    });
  }
  enablerClicked(control: IInput) {
    if (control.value) {
      control.value = false;
    } else {
      control.value = true;
    }
    this.form = this.formService.appendToFormGroup(this.page.inputs, this.form);
  }

  getGroupEnablers() {
    const enablers = this.page.inputs.find(
      (input) => input.group_enabler_master
    );
    return enablers;
  }

  checkIfEnabled(input: IInput) {
    if (input.group_enabler_master || !this.getGroupEnablers()) {
      return true;
    }
    if (this.form.controls[input.id]) {
      return true;
    }
    // this.form = this.formService.appendToFormGroup(this.page.inputs, this.form);
  }
}
