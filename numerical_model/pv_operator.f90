! (C) Copyright 2009-2016 ECMWF.
!
! This software is licensed under the terms of the Apache Licence Version 2.0
! which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
! In applying this licence, ECMWF does not waive the privileges and immunities
! granted to it by virtue of its status as an intergovernmental organisation nor
! does it submit to any jurisdiction.

!> Potential vorticity operator

!> Applies the linear operator part of the PV calculation:
!! \f{eqnarray*}{
!! q_1 &=& \nabla^2 \psi_1 - F_1 (\psi_1 -\psi_2 ) \\\\
!! q_2 &=& \nabla^2 \psi_2 - F_2 (\psi_2 -\psi_1 )
!! \f}
!!
!! (Note: The full potential vorticity calculation is done in calc_pv, and
!! includes additional beta and orography terms.)

subroutine pv_operator (x,pv,nx,ny,F1,F2,deltax,deltay)

!--- The part of the pv calculation that acts on internal streamfunction.

implicit none
integer, intent(in) :: nx        !< Zonal grid dimension
integer, intent(in) :: ny        !< Meridional grid dimension
real(8), intent(in)  :: x(nx,ny,2)  !< Streamfunction
real(8), intent(out) :: pv(nx,ny,2) !< Result of applying the operator to x
real(8), intent(in) :: F1           !< Parameter in the PV operator
real(8), intent(in) :: F2           !< Parameter in the PV operator
real(8), intent(in) :: deltax       !< Zonal grid spacing (non-dimensional)
real(8), intent(in) :: deltay       !< Meridional grid spacing (non-dimensional)

!--- del-squared of the streamfunction

call laplacian_2d (x(:,:,1),pv(:,:,1),nx,ny,deltax,deltay)
call laplacian_2d (x(:,:,2),pv(:,:,2),nx,ny,deltax,deltay)

!--- vertical differences:

pv(:,:,1) = pv(:,:,1) -F1*(x(:,:,1)-x(:,:,2))
pv(:,:,2) = pv(:,:,2) -F2*(x(:,:,2)-x(:,:,1))

end subroutine pv_operator
