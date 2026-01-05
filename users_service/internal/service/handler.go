package service

import (
    "context"
    "database/sql"

    "google.golang.org/grpc/status"
    "google.golang.org/grpc/codes"

    pb "users_service/pb"
)

type UserServer struct {
    pb.UnimplementedUserServiceServer
    DB *sql.DB
}

func NewUserService(db *sql.DB) *UserServer {
    return &UserServer{DB: db}
}

// Função auxiliar para identificar role do requisitante através do token.
func (s *UserServer) getRequesterRole(ctx context.Context, token int32) (pb.UserType, error) {
	if token == 0 {
        return pb.UserType_UNKNOWN_ROLE, status.Error(codes.Unauthenticated, "login obrigatório")
    }

    var roleStr string
    query := `SELECT tipo FROM usuario WHERE id = $1`
    err := s.DB.QueryRowContext(ctx, query, token).Scan(&roleStr)

    if err == sql.ErrNoRows {
        return pb.UserType_UNKNOWN_ROLE, status.Error(codes.PermissionDenied, "token inválido")
    }
    if err != nil {
        return pb.UserType_UNKNOWN_ROLE, status.Error(codes.Internal, "erro interno no servidor")
    }

    return stringToRole(roleStr), nil
}

// Função auxiliar para converter string do banco para ENUM do proto.
func stringToRole(roleStr string) pb.UserType {
    switch roleStr {
    case "ADMINISTRADOR":
        return pb.UserType_ADMINISTRADOR
    case "MEDICO":
        return pb.UserType_MEDICO
    case "RECEPCIONISTA":
        return pb.UserType_RECEPCIONISTA
    case "PACIENTE":
        return pb.UserType_PACIENTE
    default:
        return pb.UserType_UNKNOWN_ROLE
    }
}