package service

import (
    "context"
    "database/sql"

    "golang.org/x/crypto/bcrypt"

    "google.golang.org/grpc/status"
    "google.golang.org/grpc/codes"

    pb "users_service/pb"
)

func (s *UserServer) AuthenticateUser(ctx context.Context, req *pb.AuthRequest) (*pb.AuthResponse, error) {
    if req.Email == "" || req.Password == "" {
        return nil, status.Error(codes.InvalidArgument, "email e senha são obrigatórios")
    }

    var id int32
    var name, hashedPassword, tipoStr string

    query := `SELECT id, nome, senha, tipo FROM usuario WHERE email = $1`
    err := s.DB.QueryRowContext(ctx, query, req.Email).Scan(&id, &name, &hashedPassword, &tipoStr)
    
    if err == sql.ErrNoRows {
        return nil, status.Error(codes.Unauthenticated, "email ou senha inválidos")
    } 
    if err != nil {
        return nil, status.Error(codes.Internal, "erro interno no servidor")
    }

    // Compara a senha informada com o hash armazenado no banco
    err = bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(req.Password))
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "email ou senha inválidos")
    }

    return &pb.AuthResponse{
        Token: id,
        UserId: id,
        Name: name,
        UserType: stringToRole(tipoStr),
    }, nil
}